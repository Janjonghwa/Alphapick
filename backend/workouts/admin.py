from django.contrib import admin

from .models import WorkoutRecord


@admin.register(WorkoutRecord)
class WorkoutRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "distance_km", "duration_min", "started_at")
    search_fields = ("user__username", "course__name")
