from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recommendations.services import similar_courses

from .models import Course, FitnessSpot
from .serializers import CourseDetailSerializer, CourseListSerializer, FitnessSpotSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.select_related("category").all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        q = params.get("q") or params.get("search")
        category = params.get("category")
        region = params.get("region")
        difficulty = params.get("difficulty")
        min_distance = params.get("min_distance")
        max_distance = params.get("max_distance")
        max_duration = params.get("max_duration")

        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(region__icontains=q) | Q(description__icontains=q))
        if category:
            queryset = queryset.filter(Q(category__name=category) | Q(category__display_name__icontains=category))
        if region:
            queryset = queryset.filter(region__icontains=region)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if min_distance:
            queryset = queryset.filter(distance_km__gte=min_distance)
        if max_distance:
            queryset = queryset.filter(distance_km__lte=max_distance)
        if max_duration:
            queryset = queryset.filter(duration_min__lte=max_duration)

        return queryset.order_by("-avg_rating", "-review_count", "name")

    @action(detail=True, methods=["get"])
    def similar(self, request, pk=None):
        course = self.get_object()
        candidates = similar_courses(course, limit=5)
        serializer = CourseListSerializer(candidates, many=True, context={"request": request})
        return Response(serializer.data)


class FitnessSpotViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FitnessSpotSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = FitnessSpot.objects.select_related("category").all()
        params = self.request.query_params
        q = params.get("q") or params.get("search")
        equipment = params.get("equipment")

        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(address__icontains=q) | Q(description__icontains=q))
        if equipment:
            queryset = queryset.filter(equipment_types__icontains=equipment)

        lat = params.get("lat")
        lng = params.get("lng")
        radius_km = float(params.get("radius_km", 5))
        if lat and lng:
            from recommendations.services import filter_spots_nearby

            return filter_spots_nearby(queryset, float(lat), float(lng), radius_km)

        return queryset.order_by("-avg_rating", "-review_count", "name")
