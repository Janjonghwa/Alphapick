from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class OutfitUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("OUTFIT profile", {"fields": ("nickname", "level", "preferred_location", "preferred_categories", "onboarding_completed")}),
    )
    list_display = ("username", "email", "nickname", "level", "preferred_location", "onboarding_completed", "is_staff")
