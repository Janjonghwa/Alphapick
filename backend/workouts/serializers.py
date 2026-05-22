from rest_framework import serializers

from catalog.serializers import CourseListSerializer

from .models import WorkoutRecord


class WorkoutRecordSerializer(serializers.ModelSerializer):
    course_detail = CourseListSerializer(source="course", read_only=True)

    class Meta:
        model = WorkoutRecord
        fields = (
            "id",
            "user",
            "course",
            "course_detail",
            "distance_km",
            "duration_min",
            "memo",
            "started_at",
            "created_at",
        )
        read_only_fields = ("id", "user", "course_detail", "created_at")

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
