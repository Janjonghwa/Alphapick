from django.contrib import admin

from .models import Bookmark, Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "fitness_spot", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("content", "user__username", "course__name", "fitness_spot__name")


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "fitness_spot", "created_at")
    search_fields = ("user__username", "course__name", "fitness_spot__name")
