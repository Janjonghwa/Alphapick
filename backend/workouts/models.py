from django.conf import settings
from django.db import models


class WorkoutRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workout_records")
    course = models.ForeignKey("catalog.Course", on_delete=models.CASCADE, related_name="workout_records")
    distance_km = models.FloatField()
    duration_min = models.PositiveIntegerField()
    memo = models.TextField(blank=True)
    started_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-started_at",)

    def __str__(self):
        return f"{self.user_id}:{self.course_id}:{self.started_at:%Y-%m-%d}"
