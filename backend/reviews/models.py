from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    course = models.ForeignKey("catalog.Course", on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    fitness_spot = models.ForeignKey("catalog.FitnessSpot", on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    content = models.TextField()
    photo = models.ImageField(upload_to="review_photos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.CheckConstraint(
                check=(Q(course__isnull=False) & Q(fitness_spot__isnull=True)) | (Q(course__isnull=True) & Q(fitness_spot__isnull=False)),
                name="review_exactly_one_target",
            ),
            models.UniqueConstraint(fields=("user", "course"), condition=Q(course__isnull=False), name="unique_user_course_review"),
            models.UniqueConstraint(fields=("user", "fitness_spot"), condition=Q(fitness_spot__isnull=False), name="unique_user_spot_review"),
        ]

    def __str__(self):
        return f"{self.user_id}:{self.rating}"

    def save(self, *args, **kwargs):
        old_targets = []
        if self.pk:
            old = Review.objects.filter(pk=self.pk).first()
            if old:
                old_targets = [old.course, old.fitness_spot]
        super().save(*args, **kwargs)
        for target in old_targets + [self.course, self.fitness_spot]:
            if target:
                target.refresh_rating_cache()

    def delete(self, *args, **kwargs):
        targets = [self.course, self.fitness_spot]
        result = super().delete(*args, **kwargs)
        for target in targets:
            if target:
                target.refresh_rating_cache()
        return result


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks")
    course = models.ForeignKey("catalog.Course", on_delete=models.CASCADE, related_name="bookmarks", null=True, blank=True)
    fitness_spot = models.ForeignKey("catalog.FitnessSpot", on_delete=models.CASCADE, related_name="bookmarks", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.CheckConstraint(
                check=(Q(course__isnull=False) & Q(fitness_spot__isnull=True)) | (Q(course__isnull=True) & Q(fitness_spot__isnull=False)),
                name="bookmark_exactly_one_target",
            ),
            models.UniqueConstraint(fields=("user", "course"), condition=Q(course__isnull=False), name="unique_user_course_bookmark"),
            models.UniqueConstraint(fields=("user", "fitness_spot"), condition=Q(fitness_spot__isnull=False), name="unique_user_spot_bookmark"),
        ]

    def __str__(self):
        return f"{self.user_id}:bookmark"
