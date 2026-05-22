from django.db import models
from django.db.models import Q


class Category(models.Model):
    class Name(models.TextChoices):
        WALKING = "WALKING", "Walking"
        CYCLING = "CYCLING", "Cycling"
        HIKING = "HIKING", "Hiking"
        FITNESS_SPOT = "FITNESS_SPOT", "Fitness Spot"

    name = models.CharField(max_length=30, choices=Name.choices, unique=True)
    display_name = models.CharField(max_length=40)
    icon = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.display_name


class Course(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "EASY", "Easy"
        MEDIUM = "MEDIUM", "Medium"
        HARD = "HARD", "Hard"

    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="courses")
    description = models.TextField(blank=True)
    distance_km = models.FloatField(default=0)
    duration_min = models.PositiveIntegerField(default=0)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.EASY)
    cycle_type = models.CharField(max_length=40, blank=True)
    region = models.CharField(max_length=100, db_index=True)
    start_lat = models.FloatField(db_index=True)
    start_lng = models.FloatField(db_index=True)
    gpx_simplified = models.JSONField(default=list, blank=True)
    gpx_original_url = models.URLField(blank=True)
    source = models.CharField(max_length=40)
    external_id = models.CharField(max_length=100, blank=True)
    avg_rating = models.FloatField(default=0)
    review_count = models.PositiveIntegerField(default=0)
    nearby_parking = models.TextField(blank=True, null=True)
    nearby_transit = models.TextField(blank=True, null=True)
    traveler_info = models.TextField(blank=True, null=True)
    toilet_info = models.TextField(blank=True, null=True)
    convenience_info = models.TextField(blank=True, null=True)
    accessibility_sources = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)
        indexes = [
            models.Index(fields=("start_lat", "start_lng")),
            models.Index(fields=("category", "difficulty", "region")),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("source", "external_id"),
                condition=~Q(external_id=""),
                name="unique_course_source_external_id",
            )
        ]

    def __str__(self):
        return self.name

    def refresh_rating_cache(self):
        aggregate = self.reviews.aggregate(avg=models.Avg("rating"), count=models.Count("id"))
        self.avg_rating = round(aggregate["avg"] or 0, 2)
        self.review_count = aggregate["count"] or 0
        self.save(update_fields=("avg_rating", "review_count"))


class FitnessSpot(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="fitness_spots")
    equipment_types = models.JSONField(default=list, blank=True)
    lat = models.FloatField(db_index=True)
    lng = models.FloatField(db_index=True)
    address = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    source = models.CharField(max_length=40, default="PUBLIC_DATA")
    external_id = models.CharField(max_length=100, blank=True)
    avg_rating = models.FloatField(default=0)
    review_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)
        indexes = [
            models.Index(fields=("lat", "lng")),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("source", "external_id"),
                condition=~Q(external_id=""),
                name="unique_spot_source_external_id",
            )
        ]

    def __str__(self):
        return self.name

    def refresh_rating_cache(self):
        aggregate = self.reviews.aggregate(avg=models.Avg("rating"), count=models.Count("id"))
        self.avg_rating = round(aggregate["avg"] or 0, 2)
        self.review_count = aggregate["count"] or 0
        self.save(update_fields=("avg_rating", "review_count"))
