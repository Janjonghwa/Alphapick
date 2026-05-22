from rest_framework import serializers

from .models import Category, Course, FitnessSpot


ACCESSIBILITY_FIELDS = (
    ("nearby_parking", "주차장"),
    ("nearby_transit", "대중교통"),
    ("traveler_info", "여행자 안내"),
    ("toilet_info", "화장실"),
    ("convenience_info", "편의시설"),
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "display_name", "icon")


class CourseListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "name",
            "category",
            "distance_km",
            "duration_min",
            "difficulty",
            "region",
            "start_lat",
            "start_lng",
            "avg_rating",
            "review_count",
            "is_bookmarked",
        )

    def get_is_bookmarked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.bookmarks.filter(user=request.user).exists()


class CourseDetailSerializer(CourseListSerializer):
    accessibility_info = serializers.SerializerMethodField()

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + (
            "description",
            "cycle_type",
            "gpx_simplified",
            "gpx_original_url",
            "source",
            "external_id",
            "accessibility_info",
            "created_at",
        )

    def get_accessibility_info(self, obj):
        sources = obj.accessibility_sources or {}
        items = []
        for field, label in ACCESSIBILITY_FIELDS:
            value = getattr(obj, field)
            items.append(
                {
                    "key": field,
                    "label": label,
                    "value": value,
                    "display_value": value or "정보 없음",
                    "source": sources.get(field),
                }
            )
        return items


class FitnessSpotSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.filter(name=Category.Name.FITNESS_SPOT),
        write_only=True,
        required=False,
    )
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = FitnessSpot
        fields = (
            "id",
            "name",
            "category",
            "category_id",
            "equipment_types",
            "lat",
            "lng",
            "address",
            "description",
            "source",
            "external_id",
            "avg_rating",
            "review_count",
            "is_bookmarked",
            "created_at",
        )
        read_only_fields = ("avg_rating", "review_count", "created_at")

    def get_is_bookmarked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.bookmarks.filter(user=request.user).exists()
