from django.conf import settings
from django.db import models
from django.db.models.functions import Lower

# Create your models here.

class Todo(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class PersonalCourse(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=60, default="Personal course")
    credits = models.PositiveSmallIntegerField(default=3)
    prerequisites = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                Lower("code"), "user", name="unique_personal_course_code_per_user"
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class CalendarEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course_code = models.CharField(max_length=20)
    course_name = models.CharField(max_length=120)
    title = models.CharField(max_length=120)
    event_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    description = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["event_date", "start_time", "title"]

    def __str__(self):
        return f"{self.title} ({self.event_date})"