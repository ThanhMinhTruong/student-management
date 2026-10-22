# Troy / HUST Student Resource Hub

An independent student resource hub for the Troy University program at Hanoi University of Science and Technology (HUST). It provides sign-in, a curated course catalog, links to student-maintained course materials, and a monthly study planner.

This is not an official university service or the Canvas LMS. Course information and materials are maintained by the community. Verify course offerings, prerequisites, and deadlines with the program and current syllabi.

## Resource source

The course names and links in this app are based on the public [Troy University Resources repository](https://github.com/lcvp/troy-hust-university-resources). The app displays a curated subset of its curriculum and links to the upstream folders; it does not copy or host the repository's documents.

## Features

- Account registration, login, and logout using Django authentication.
- Authenticated dashboard with selected courses and links to program resources.
- Course catalog with credits, categories, prerequisites, and links to each course folder.
- Monthly study planner. The public repository does not provide a verified assignment deadline feed, so the planner does not invent deadlines.
- Responsive templates and static files served with WhiteNoise.

## Routes

| Page | URL |
| --- | --- |
| Home | `/` |
| Dashboard | `/myapp/dashboard/` |
| Course resources | `/myapp/courses/` |
| Study planner | `/myapp/calendar/` |
| Sign in | `/myapp/login/` |
| Create account | `/myapp/signup/` |
| Django admin | `/admin/` |

The dashboard, courses, and study planner require an authenticated account. After signup or login, users are redirected to the dashboard.

## Local development

Requirements: Python 3.12.8 (see `.python-version`). From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. For local development, Django uses the `db.sqlite3` database unless `DATABASE_URL` is set. To create an administrator account for `/admin/`, run:

```powershell
python manage.py createsuperuser
```

Run the tests with:

```powershell
python manage.py test firstapp.tests
```

## Render deployment

The root `render.yaml` is a Render Blueprint defining a Python web service and a PostgreSQL database. In Render, create or sync a Blueprint from this repository's `main` branch and select the root `render.yaml` file.

The Blueprint configures:

- Build: `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate`
- Start: `gunicorn mysite.wsgi:application`
- PostgreSQL connection through the service's `DATABASE_URL` environment variable
- A generated `SECRET_KEY` and production HTTPS/cookie settings

To configure the existing Render services from the Blueprint, associate the web service with the Blueprint and create/link the database resource. The build command applies Django migrations to that database. Student accounts are stored in PostgreSQL on Render; local SQLite data is separate and is not copied automatically.

Do not commit database URLs, passwords, or other secrets. Keep `DEBUG=False` in production.

## Stack

- Python 3.12.8
- Django 5.2
- PostgreSQL on Render; SQLite for local development
- Gunicorn and WhiteNoise

- Site:https://student-management-wq1b.onrender.com
