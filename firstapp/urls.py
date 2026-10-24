from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("calendar/events/<int:event_id>/delete/", views.delete_calendar_event, name="delete_calendar_event"),
    path("courses/", views.courses_view, name="courses"),
    path("login/", views.AppLoginView.as_view(), name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
]

