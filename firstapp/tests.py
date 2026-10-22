from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


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
		self.assertContains(response, "Ecology &amp; Evolution")
		self.assertContains(response, "Welcome back, Casey")

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
		self.assertContains(response, "Problem Set 6")
		self.assertContains(response, "Field observations journal")

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
		self.assertContains(response, "Ecology &amp; Evolution")
		self.assertContains(response, "Statistics for Research")
