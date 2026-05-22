from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Level(models.TextChoices):
        EASY = "EASY", "Easy"
        MEDIUM = "MEDIUM", "Medium"
        HARD = "HARD", "Hard"

    nickname = models.CharField(max_length=40, blank=True)
    level = models.CharField(max_length=10, choices=Level.choices, default=Level.EASY)
    preferred_location = models.CharField(max_length=100, blank=True)
    preferred_categories = models.JSONField(default=list, blank=True)
    onboarding_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def display_name(self):
        return self.nickname or self.username
