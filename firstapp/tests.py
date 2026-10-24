from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import CalendarEvent, PersonalCourse


class CanvasDashboardTests(TestCase):
	def setUp(self):
		self.password = "test-password-123"
		self.user = get_user_model().objects.create_user(
			username="student",
			password=self.password,
			first_name="Casey",
		)

	def test_login_redirects_to_dashboard(self):
		response = self.client.post(reverse("login"), {
			"username": self.user.username,
			"password": self.password,
		})

		self.assertRedirects(response, reverse("dashboard"))

	def test_signup_creates_and_logs_in_user(self):
		response = self.client.post(reverse("signup"), {
			"username": "newstudent",
			"password1": "A-strong-password-9274",
			"password2": "A-strong-password-9274",
		})

		self.assertRedirects(response, reverse("dashboard"))
		self.assertTrue(
			get_user_model().objects.filter(username="newstudent").exists()
		)
		dashboard = self.client.get(reverse("dashboard"))
		self.assertEqual(dashboard.status_code, 200)

	def test_signup_rejects_mismatched_passwords(self):
		response = self.client.post(reverse("signup"), {
			"username": "newstudent",
			"password1": "A-strong-password-9274",
			"password2": "A-different-password-9274",
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "The two password fields")
		self.assertFalse(
			get_user_model().objects.filter(username="newstudent").exists()
		)

	def test_dashboard_requires_authentication(self):
		response = self.client.get(reverse("dashboard"))

		self.assertRedirects(
			response,
			f"{reverse('login')}?next={reverse('dashboard')}",
		)

	def test_signed_in_dashboard_renders_course_content(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse("dashboard"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "The University Experience")
		self.assertContains(response, "Welcome back, Casey")
		self.assertContains(response, "Program course plan")

	def test_calendar_requires_authentication(self):
		response = self.client.get(reverse("calendar"))

		self.assertRedirects(
			response,
			f"{reverse('login')}?next={reverse('calendar')}",
		)

	def test_calendar_shows_month_and_deadlines(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse("calendar"), {"month": "2026-10"})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "October 2026")
		self.assertContains(response, "No events this month")
		self.assertContains(response, "Schedule a course session")

	def test_courses_requires_authentication(self):
		response = self.client.get(reverse("courses"))

		self.assertRedirects(
			response,
			f"{reverse('login')}?next={reverse('courses')}",
		)

	def test_courses_page_shows_course_list(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse("courses"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Computer Science I")
		self.assertContains(response, "Data Structures")
		self.assertContains(response, "lcvp/troy-hust-university-resources/tree/main/CS-2250")

	def test_custom_course_can_be_added_and_scheduled(self):
		self.client.force_login(self.user)
		response = self.client.post(reverse("courses"), {
			"action": "create_course",
			"code": "math-2200",
			"name": "Linear Algebra",
			"category": "Mathematics",
			"credits": 3,
			"prerequisites": "MTH-1112",
		})

		self.assertRedirects(response, reverse("courses"))
		course = PersonalCourse.objects.get(user=self.user, code="MATH-2200")
		response = self.client.post(reverse("courses"), {
			"action": "schedule_event",
			"course_key": f"custom-{course.pk}",
			"title": "Linear algebra review",
			"event_date": "2026-10-24",
			"start_time": "14:00",
			"end_time": "15:30",
			"description": "Chapter 2",
		})

		self.assertRedirects(response, reverse("calendar"))
		event = CalendarEvent.objects.get(user=self.user)
		self.assertEqual(event.course_name, "Linear Algebra")
		calendar = self.client.get(reverse("calendar"), {"month": "2026-10"})
		self.assertContains(calendar, "Linear algebra review")
		self.assertContains(calendar, "2:00 PM")

	def test_calendar_events_are_private_and_can_be_removed(self):
		self.client.force_login(self.user)
		event = CalendarEvent.objects.create(
			user=self.user,
			course_code="CS-2250",
			course_name="Computer Science I",
			title="Project work",
			event_date="2026-10-24",
		)
		other_user = get_user_model().objects.create_user(
			username="anotherstudent", password=self.password
		)
		CalendarEvent.objects.create(
			user=other_user,
			course_code="CS-2250",
			course_name="Computer Science I",
			title="Private event",
			event_date="2026-10-24",
		)

		calendar = self.client.get(reverse("calendar"), {"month": "2026-10"})
		self.assertContains(calendar, "Project work")
		self.assertNotContains(calendar, "Private event")
		response = self.client.post(
			reverse("delete_calendar_event", args=[event.pk])
		)
		self.assertRedirects(response, "/myapp/calendar/?month=2026-10")
		self.assertFalse(CalendarEvent.objects.filter(pk=event.pk).exists())
