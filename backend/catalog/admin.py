from django.contrib import admin

from .models import Category, Course, FitnessSpot


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "display_name", "icon")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "region", "difficulty", "distance_km", "avg_rating", "review_count")
    list_filter = ("category", "difficulty", "region", "source")
    search_fields = ("name", "region", "external_id")


@admin.register(FitnessSpot)
class FitnessSpotAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "avg_rating", "review_count")
    search_fields = ("name", "address", "external_id")
