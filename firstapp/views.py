from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from calendar import monthcalendar
from datetime import date, datetime, timedelta

COURSES = [
    {
        "code": "BIO 214",
        "name": "Ecology & Evolution",
        "instructor": "Dr. Elise Warren",
        "room": "Science Hall 204",
        "accent": "fern",
        "schedule": "Mon, Wed · 10:00 AM",
    },
    {
        "code": "HIST 308",
        "name": "Cities of the Modern World",
        "instructor": "Prof. Marcus Lee",
        "room": "Hawthorne 118",
        "accent": "clay",
        "schedule": "Tue, Thu · 1:30 PM",
    },
    {
        "code": "STAT 201",
        "name": "Statistics for Research",
        "instructor": "Dr. Priya Shah",
        "room": "Online course",
        "accent": "ocean",
        "schedule": "Online · Asynchronous",
    },
    {
        "code": "WRIT 220",
        "name": "Writing in the Disciplines",
        "instructor": "Prof. Jordan Kim",
        "room": "Arts Center 32",
        "accent": "gold",
        "schedule": "Mon, Wed · 2:00 PM",
    },
]

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


@login_required(login_url="login")
def dashboard(request):
    assignments = [
        {
            "day": "23",
            "month": "OCT",
            "course": "STAT 201",
            "title": "Problem Set 6",
            "time": "11:59 PM",
        },
        {
            "day": "24",
            "month": "OCT",
            "course": "BIO 214",
            "title": "Field observations journal",
            "time": "5:00 PM",
        },
        {
            "day": "27",
            "month": "OCT",
            "course": "HIST 308",
            "title": "Primary source response",
            "time": "9:00 AM",
        },
    ]
    return render(request, "firstapp/dashboard.html", {
        "courses": COURSES,
        "assignments": assignments,
    })


@login_required(login_url="login")
def courses_view(request):
    return render(request, "firstapp/courses.html", {"courses": COURSES})


@login_required(login_url="login")
def calendar_view(request):
    month_value = request.GET.get("month", "2026-10")
    try:
        month_start = datetime.strptime(month_value, "%Y-%m").date().replace(day=1)
    except ValueError:
        month_start = date(2026, 10, 1)

    deadlines = {
        date(2026, 10, 23): {
            "course": "STAT 201",
            "title": "Problem Set 6",
            "time": "11:59 PM",
            "accent": "ocean",
        },
        date(2026, 10, 24): {
            "course": "BIO 214",
            "title": "Field observations journal",
            "time": "5:00 PM",
            "accent": "fern",
        },
        date(2026, 10, 27): {
            "course": "HIST 308",
            "title": "Primary source response",
            "time": "9:00 AM",
            "accent": "clay",
        },
    }
    weeks = [
        [
            {
                "number": day_number,
                "events": [deadlines[date(month_start.year, month_start.month, day_number)]]
                if date(month_start.year, month_start.month, day_number) in deadlines
                else [],
            } if day_number else None
            for day_number in week
        ]
        for week in monthcalendar(month_start.year, month_start.month)
    ]
    previous_month = (month_start - timedelta(days=1)).strftime("%Y-%m")
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1).strftime("%Y-%m")

    return render(request, "firstapp/calendar.html", {
        "month_name": month_start.strftime("%B %Y"),
        "month_value": month_start.strftime("%Y-%m"),
        "previous_month": previous_month,
        "next_month": next_month,
        "weeks": weeks,
        "deadline_count": sum(len(day["events"]) for week in weeks for day in week if day),
    })


class AppLoginView(LoginView):
    template_name = "firstapp/login.html"
    redirect_authenticated_user = True

