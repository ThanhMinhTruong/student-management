from calendar import monthcalendar
from datetime import date, datetime, timedelta

from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render


RESOURCE_ROOT = "https://github.com/lcvp/troy-hust-university-resources"

COURSES = [
    {
        "code": "TROY-1101",
        "name": "The University Experience",
        "credits": 1,
        "category": "General studies",
        "prerequisites": "None listed",
        "accent": "gold",
    },
    {
        "code": "ENG-1101",
        "name": "Composition and Modern English I",
        "credits": 3,
        "category": "General studies",
        "prerequisites": "None listed",
        "accent": "clay",
    },
    {
        "code": "ART-1133",
        "name": "Visual Arts",
        "credits": 2,
        "category": "General studies",
        "prerequisites": "None listed",
        "accent": "ocean",
    },
    {
        "code": "MTH-1112",
        "name": "Pre-Calculus Algebra",
        "credits": 3,
        "category": "Mathematics",
        "prerequisites": "None listed",
        "accent": "fern",
    },
    {
        "code": "CS-2250",
        "name": "Computer Science I",
        "credits": 3,
        "category": "Computer science core",
        "prerequisites": "MTH-1112",
        "accent": "clay",
    },
    {
        "code": "CS-2255",
        "name": "Computer Science II",
        "credits": 3,
        "category": "Computer science core",
        "prerequisites": "CS-2250",
        "accent": "ocean",
    },
    {
        "code": "CS-3323",
        "name": "Data Structures",
        "credits": 3,
        "category": "Computer science core",
        "prerequisites": "CS-2255, MTH-1125, MTH-2215",
        "accent": "fern",
    },
    {
        "code": "CS-3332",
        "name": "Software Engineering I",
        "credits": 3,
        "category": "Computer science core",
        "prerequisites": "CS-3323",
        "accent": "gold",
    },
    {
        "code": "CS-4420",
        "name": "Introduction to Database Systems",
        "credits": 3,
        "category": "Computer science core",
        "prerequisites": "CS-3323",
        "accent": "ocean",
    },
    {
        "code": "CS-4445",
        "name": "Data Communication and Networking",
        "credits": 3,
        "category": "Computer science core",
        "prerequisites": "CS-3323",
        "accent": "clay",
    },
    {
        "code": "CS-3331",
        "name": "Fundamentals of Artificial Intelligence",
        "credits": 3,
        "category": "Computer science elective",
        "prerequisites": "CS-3323",
        "accent": "fern",
    },
    {
        "code": "CS-4410",
        "name": "Introduction to Machine Learning",
        "credits": 3,
        "category": "Computer science elective",
        "prerequisites": "CS-3323",
        "accent": "gold",
    },
    {
        "code": "STAT-2210",
        "name": "Introductory Statistics",
        "credits": 3,
        "category": "Mathematics and science",
        "prerequisites": "MTH-1112",
        "accent": "ocean",
    },
]

for course in COURSES:
    course["resources_url"] = f"{RESOURCE_ROOT}/tree/main/{course['code']}"

RESOURCE_LINKS = [
    {
        "title": "Program course plan",
        "description": "Browse the degree plan, prerequisites, and course sequence.",
        "url": RESOURCE_ROOT,
        "label": "Open course plan",
    },
    {
        "title": "Study notes",
        "description": "Find shared notes and general study references.",
        "url": f"{RESOURCE_ROOT}/blob/main/Miscellaneous/Notes.md",
        "label": "Browse notes",
    },
    {
        "title": "Program documents",
        "description": "Open the repository's program-level documents.",
        "url": f"{RESOURCE_ROOT}/tree/main/Miscellaneous/Program-Documents",
        "label": "View documents",
    },
]


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        auth_login(request, user)
        return redirect("dashboard")

    return render(request, "firstapp/signup.html", {"form": form})


@login_required(login_url="login")
def dashboard(request):
    return render(request, "firstapp/dashboard.html", {
        "courses": COURSES[:4],
        "course_count": len(COURSES),
        "resource_links": RESOURCE_LINKS,
    })


@login_required(login_url="login")
def courses_view(request):
    return render(request, "firstapp/courses.html", {"courses": COURSES})


@login_required(login_url="login")
def calendar_view(request):
    month_value = request.GET.get("month", date.today().strftime("%Y-%m"))
    try:
        month_start = datetime.strptime(month_value, "%Y-%m").date().replace(day=1)
    except ValueError:
        month_start = date.today().replace(day=1)

    weeks = [
        [
            {"number": day_number, "events": []} if day_number else None
            for day_number in week
        ]
        for week in monthcalendar(month_start.year, month_start.month)
    ]
    previous_month = (month_start - timedelta(days=1)).strftime("%Y-%m")
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1).strftime("%Y-%m")

    return render(request, "firstapp/calendar.html", {
        "month_name": month_start.strftime("%B %Y"),
        "previous_month": previous_month,
        "next_month": next_month,
        "weeks": weeks,
        "deadline_count": 0,
    })


class AppLoginView(LoginView):
    template_name = "firstapp/login.html"
    redirect_authenticated_user = True
