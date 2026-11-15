import os
import time
import ctypes
from ctypes import wintypes

import psutil

from django.core.management.base import BaseCommand
from django.utils import timezone

from tracker.models import UsageSample
from tracker.services import categorize_app


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("dwTime", wintypes.DWORD),
    ]


class WindowsActivityMonitor:

    def __init__(self):
        if os.name != "nt":
            raise OSError("This tracker currently supports Windows only.")

        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

        self.user32.GetForegroundWindow.restype = wintypes.HWND

        self.user32.GetWindowThreadProcessId.argtypes = [
            wintypes.HWND,
            ctypes.POINTER(wintypes.DWORD),
        ]

        self.kernel32.GetTickCount.restype = wintypes.DWORD

    def get_foreground_app(self):
        hwnd = self.user32.GetForegroundWindow()

        if not hwnd:
            return None

        process_id = wintypes.DWORD()

        self.user32.GetWindowThreadProcessId(
            hwnd,
            ctypes.byref(process_id)
        )

        if not process_id.value:
            return None

        try:
            return psutil.Process(process_id.value).name()

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    def get_idle_seconds(self):
        info = LASTINPUTINFO()
        info.cbSize = ctypes.sizeof(LASTINPUTINFO)

        success = self.user32.GetLastInputInfo(ctypes.byref(info))

        if not success:
            return 0

        current_tick = self.kernel32.GetTickCount()

        elapsed_ms = (current_tick - info.dwTime) & 0xFFFFFFFF

        return elapsed_ms / 1000


class Command(BaseCommand):

    help = "Monitor foreground Windows applications and record usage."

    def add_arguments(self, parser):
        parser.add_argument(
            "--interval",
            type=float,
            default=1,
            help="Polling interval in seconds."
        )

        parser.add_argument(
            "--idle-seconds",
            type=int,
            default=60,
            help="Seconds without keyboard or mouse input before pausing tracking."
        )

        parser.add_argument(
            "--minutes",
            type=int,
            default=0,
            help="Optional monitoring duration in minutes."
        )

    def save_usage(self, app_name, duration, started_at):

        duration = int(round(duration))

        if duration < 1:
            return

        duration = min(duration, 65535)

        category = categorize_app(app_name)

        UsageSample.objects.create(
            app_name=app_name,
            category=category,
            captured_at=started_at,
            duration_seconds=duration
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Saved: {app_name} - {duration}s ({category})"
            )
        )

    def handle(self, *args, **options):

        interval = options["interval"]
        idle_limit = options["idle_seconds"]
        minutes = options["minutes"]

        if interval <= 0:
            self.stderr.write("Polling interval must be greater than zero.")
            return

        if idle_limit < 1:
            self.stderr.write("Idle threshold must be at least one second.")
            return

        monitor = WindowsActivityMonitor()

        active_app = None
        active_since = None
        active_started_at = None

        start_time = time.monotonic()

        deadline = (
            start_time + minutes * 60
            if minutes > 0
            else None
        )

        self.stdout.write(
            self.style.SUCCESS(
                "LifeTraceIQ monitoring started. Press Ctrl+C to stop."
            )
        )

        try:
            while True:

                now = time.monotonic()

                if deadline and now >= deadline:
                    break

                idle_seconds = monitor.get_idle_seconds()

                if idle_seconds >= idle_limit:
                    current_app = None
                else:
                    current_app = monitor.get_foreground_app()

                if current_app != active_app:

                    if active_app and active_since is not None:
                        duration = now - active_since

                        self.save_usage(
                            active_app,
                            duration,
                            active_started_at
                        )

                    active_app = current_app

                    if active_app:
                        active_since = now
                        active_started_at = timezone.now()

                    else:
                        active_since = None
                        active_started_at = None

                time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write("\nStopping monitor...")

        finally:
            if active_app and active_since is not None:

                duration = time.monotonic() - active_since

                self.save_usage(
                    active_app,
                    duration,
                    active_started_at
                )

            self.stdout.write(
                self.style.SUCCESS("LifeTraceIQ monitoring stopped.")
            )