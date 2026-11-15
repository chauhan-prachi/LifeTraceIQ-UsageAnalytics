# LifeTraceIQ

**Understand your digital habits. Reclaim your time.**

LifeTraceIQ is a local-first Windows desktop application usage analytics system. It monitors foreground application activity, estimates time spent in different applications, categorizes usage, and presents insights through a Django dashboard and JSON API.

The project explores how Python, Django, PostgreSQL, operating-system APIs, and data analytics can work together to build a practical digital behaviour monitoring system.

## Features

- **Application monitoring:** Detects the currently active Windows desktop application.
- **Usage tracking:** Records application names, timestamps, categories, and estimated usage durations.
- **Application categorization:** Classifies applications into productive, social media, entertainment, browsing, and other categories.
- **Custom categorization:** Allows application categories to be managed through Django Admin.
- **Usage dashboard:** Displays daily tracked time, productive time, distracting time, category breakdowns, and frequently used applications.
- **JSON API:** Exposes daily usage summaries through `/api/summary/`.
- **Database support:** Supports SQLite and PostgreSQL.
- **Local-first design:** Stores usage records in a locally configured database.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | Django |
| Database | PostgreSQL / SQLite |
| Database Integration | Django ORM, Psycopg |
| Application Monitoring | Windows API, ctypes |
| Process Information | psutil |
| Frontend | HTML, CSS |
| Configuration | python-dotenv |

## Project Structure

```text
LifeTraceIQ/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── tracker/
│   ├── management/
│   │   └── commands/
│   │       └── track_usage.py
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── services.py
│   └── views.py
│
├── templates/
│   └── tracker/
│       └── dashboard.html
│
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Getting Started

### 1. Clone the repository

```powershell
git clone <YOUR_REPOSITORY_URL>
cd LifeTraceIQ
```

### 2. Create a virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

```powershell
Copy-Item .env.example .env
```

The default configuration uses SQLite, so no separate database server is required.

Update `SECRET_KEY` before using the application beyond local development.

### 5. Apply database migrations

```powershell
python manage.py migrate
```

### 6. Create an administrator account (optional)

```powershell
python manage.py createsuperuser
```

### 7. Start the Django server

```powershell
python manage.py runserver
```

Open the dashboard:

```text
http://127.0.0.1:8000/
```

Django Admin:

```text
http://127.0.0.1:8000/admin/
```

## Using the Application Monitor

LifeTraceIQ's monitoring command runs separately from the Django web server.

Open another PowerShell window, activate the virtual environment, and run:

```powershell
python manage.py track_usage --interval 5
```

The monitor samples the foreground application every five seconds.

To run monitoring for 30 minutes:

```powershell
python manage.py track_usage --interval 5 --minutes 30
```

Press `Ctrl+C` to stop continuous monitoring.

**Note:** The monitoring component currently supports Windows only.

## PostgreSQL Configuration

LifeTraceIQ supports PostgreSQL as an alternative to SQLite.

To use PostgreSQL, configure the following variables in your local `.env` file:

```dotenv
DB_ENGINE=postgresql
DB_NAME=lifetraceiq
DB_USER=lifetraceiq_user
DB_PASSWORD=your-local-database-password
DB_HOST=127.0.0.1
DB_PORT=5432
```

Create the database and user in PostgreSQL before starting the application.

Then apply migrations:

```powershell
python manage.py migrate
```

Keep database credentials in `.env`. Never commit that file to GitHub.

## API

LifeTraceIQ provides a JSON endpoint for daily usage summaries.

**Endpoint:**

```text
GET /api/summary/
```

Open the endpoint locally:

```text
http://127.0.0.1:8000/api/summary/
```

The response includes:

- Summary date
- Total tracked seconds
- Productive usage seconds
- Distracting usage seconds
- Application usage rankings
- Category-wise usage breakdown

## Data Model

### UsageSample

Stores individual application usage samples.

| Field | Description |
|---|---|
| app_name | Foreground application name |
| category | Application usage category |
| captured_at | Timestamp of the captured sample |
| duration_seconds | Estimated duration represented by the sample |

### ApplicationCategory

Stores application categorization rules that can be managed through Django Admin.

| Field | Description |
|---|---|
| app_name | Application name |
| category | Assigned usage category |
| is_active | Whether the custom category rule is active |
| created_at | Record creation timestamp |
| updated_at | Last modification timestamp |

## Privacy and Limitations

LifeTraceIQ is designed to collect limited application activity information.

It records foreground application names and estimated usage durations. It does not collect:

- Keystrokes or typed text
- Screenshots or screen recordings
- Messages or document contents
- Browser URLs or individual website activity
- Passwords or clipboard contents

Important limitations:

- Application monitoring currently works on Windows.
- Usage durations are estimates based on periodic sampling.
- Very short application switches may be missed.
- Idle detection relies on keyboard and mouse inactivity. Passive activities, such as watching a video without interacting with the computer, may be classified as idle.
- Application categories are estimates and do not objectively measure productivity.
- The project is currently a local MVP, not a production-hardened monitoring service.

## Learning Objectives

This project demonstrates practical experience with:

1. Python application development.
2. Django models, views, templates, and management commands.
3. Relational database design and ORM operations.
4. PostgreSQL integration.
5. Operating-system process monitoring.
6. Data collection and aggregation.
7. REST-style JSON API development.
8. Environment-based configuration.
9. Building a data analytics dashboard.

## Future Improvements

- Automated unit and integration tests.
- Improved usage-duration accuracy.
- Historical usage trends and date filters.
- Configurable idle detection.
- More advanced application categorization.
- Data export functionality.
- Improved dashboard visualizations.
- Data retention and deletion controls.

---

**LifeTraceIQ — Understand your digital habits. Reclaim your time.**