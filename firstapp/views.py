from calendar import monthcalendar
from datetime import date, datetime, timedelta

from django import forms
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .models import CalendarEvent, PersonalCourse


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


class PersonalCourseForm(forms.ModelForm):
    class Meta:
        model = PersonalCourse
        fields = ["code", "name", "category", "credits", "prerequisites"]
        widgets = {
            "code": forms.TextInput(attrs={"placeholder": "e.g. CS 2100"}),
            "name": forms.TextInput(attrs={"placeholder": "Course name"}),
            "category": forms.TextInput(attrs={"placeholder": "Category"}),
            "credits": forms.NumberInput(attrs={"min": 0, "max": 20}),
            "prerequisites": forms.TextInput(attrs={"placeholder": "Optional"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data["code"].strip().upper()
        if self.user and PersonalCourse.objects.filter(
            user=self.user, code__iexact=code
        ).exists():
            raise forms.ValidationError("You already have a course with this code.")
        return code


class ScheduleEventForm(forms.Form):
    title = forms.CharField(max_length=120)
    event_date = forms.DateField(input_formats=["%Y-%m-%d"])
    start_time = forms.TimeField(required=False, input_formats=["%H:%M"])
    end_time = forms.TimeField(required=False, input_formats=["%H:%M"])
    description = forms.CharField(max_length=240, required=False)

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if start_time and end_time and end_time <= start_time:
            self.add_error("end_time", "End time must be later than start time.")
        return cleaned_data


def _course_for_schedule(user, schedule_key):
    if schedule_key.startswith("custom-"):
        try:
            course_id = int(schedule_key.removeprefix("custom-"))
        except ValueError:
            return None
        course = PersonalCourse.objects.filter(user=user, pk=course_id).first()
        if course:
            return {"code": course.code, "name": course.name}
        return None

    return next(
        (course for course in COURSES if course["code"] == schedule_key),
        None,
    )


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
    personal_course_form = PersonalCourseForm(user=request.user)
    schedule_form = None
    schedule_error_key = None

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create_course":
            personal_course_form = PersonalCourseForm(
                request.POST, user=request.user
            )
            if personal_course_form.is_valid():
                course = personal_course_form.save(commit=False)
                course.user = request.user
                course.save()
                messages.success(request, f"{course.name} was added to your courses.")
                return redirect("courses")
        elif action == "schedule_event":
            schedule_error_key = request.POST.get("course_key", "")
            schedule_form = ScheduleEventForm(request.POST)
            course = _course_for_schedule(request.user, schedule_error_key)
            if not course:
                messages.error(request, "That course could not be found.")
            elif schedule_form.is_valid():
                cleaned = schedule_form.cleaned_data
                CalendarEvent.objects.create(
                    user=request.user,
                    course_code=course["code"],
                    course_name=course["name"],
                    title=cleaned["title"],
                    event_date=cleaned["event_date"],
                    start_time=cleaned["start_time"],
                    end_time=cleaned["end_time"],
                    description=cleaned["description"],
                )
                messages.success(request, "The course session was added to your calendar.")
                return redirect("calendar")

    courses = [dict(course, schedule_key=course["code"]) for course in COURSES]
    for course in PersonalCourse.objects.filter(user=request.user):
        courses.append({
            "code": course.code,
            "name": course.name,
            "credits": course.credits,
            "category": course.category,
            "prerequisites": course.prerequisites or "None listed",
            "accent": "fern",
            "schedule_key": f"custom-{course.pk}",
            "is_custom": True,
        })

    return render(request, "firstapp/courses.html", {
        "courses": courses,
        "personal_course_form": personal_course_form,
        "schedule_form": schedule_form,
        "schedule_error_key": schedule_error_key,
        "today_iso": date.today().isoformat(),
    })


@login_required(login_url="login")
def calendar_view(request):
    month_value = request.GET.get("month", date.today().strftime("%Y-%m"))
    try:
        month_start = datetime.strptime(month_value, "%Y-%m").date().replace(day=1)
    except ValueError:
        month_start = date.today().replace(day=1)

    event_days = {}
    accent_by_code = {course["code"]: course["accent"] for course in COURSES}
    events = CalendarEvent.objects.filter(
        user=request.user,
        event_date__year=month_start.year,
        event_date__month=month_start.month,
    )
    for event in events:
        event.accent = accent_by_code.get(event.course_code, "fern")
        event_days.setdefault(event.event_date.day, []).append(event)

    weeks = [
        [
            {"number": day_number, "events": event_days.get(day_number, [])}
            if day_number else None
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
        "event_count": events.count(),
        "today_month": date.today().strftime("%Y-%m"),
    })


@login_required(login_url="login")
def delete_calendar_event(request, event_id):
    if request.method != "POST":
        return redirect("calendar")
    event = get_object_or_404(CalendarEvent, pk=event_id, user=request.user)
    month = event.event_date.strftime("%Y-%m")
    event.delete()
    messages.success(request, "The calendar event was removed.")
    return redirect(f"/myapp/calendar/?month={month}")


class AppLoginView(LoginView):
    template_name = "firstapp/login.html"
    redirect_authenticated_user = True
