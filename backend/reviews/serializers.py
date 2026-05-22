from rest_framework import serializers

from catalog.serializers import CourseListSerializer, FitnessSpotSerializer

from .models import Bookmark, Review


class ReviewSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source="user.display_name", read_only=True)

    class Meta:
        model = Review
        fields = (
            "id",
            "user",
            "user_nickname",
            "course",
            "fitness_spot",
            "rating",
            "content",
            "photo",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "user_nickname", "created_at", "updated_at")

    def validate(self, attrs):
        course = attrs.get("course", getattr(self.instance, "course", None))
        fitness_spot = attrs.get("fitness_spot", getattr(self.instance, "fitness_spot", None))
        if bool(course) == bool(fitness_spot):
            raise serializers.ValidationError("course 또는 fitness_spot 중 하나만 지정해야 합니다.")
        request = self.context.get("request")
        if request and request.user.is_authenticated and self.instance is None:
            duplicate = Review.objects.filter(user=request.user)
            if course:
                duplicate = duplicate.filter(course=course)
            if fitness_spot:
                duplicate = duplicate.filter(fitness_spot=fitness_spot)
            if duplicate.exists():
                raise serializers.ValidationError("이미 이 항목에 후기를 작성했습니다.")
        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class BookmarkSerializer(serializers.ModelSerializer):
    course_detail = CourseListSerializer(source="course", read_only=True)
    fitness_spot_detail = FitnessSpotSerializer(source="fitness_spot", read_only=True)

    class Meta:
        model = Bookmark
        fields = (
            "id",
            "course",
            "course_detail",
            "fitness_spot",
            "fitness_spot_detail",
            "created_at",
        )
        read_only_fields = ("id", "course_detail", "fitness_spot_detail", "created_at")

    def validate(self, attrs):
        course = attrs.get("course")
        fitness_spot = attrs.get("fitness_spot")
        if bool(course) == bool(fitness_spot):
            raise serializers.ValidationError("course 또는 fitness_spot 중 하나만 지정해야 합니다.")
        return attrs
