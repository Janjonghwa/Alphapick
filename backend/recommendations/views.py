from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import Course
from catalog.serializers import CourseListSerializer

from .services import filter_courses_nearby, personalized_courses


class PersonalizedRecommendationView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        courses = personalized_courses(request.user, limit=int(request.query_params.get("limit", 10)))
        serializer = CourseListSerializer(courses, many=True, context={"request": request})
        return Response(serializer.data)


class NearbyRecommendationView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        if not lat or not lng:
            return Response({"detail": "lat, lng query parameters are required."}, status=400)
        radius_km = float(request.query_params.get("radius_km", 5))
        courses = filter_courses_nearby(Course.objects.select_related("category").all(), float(lat), float(lng), radius_km)
        serializer = CourseListSerializer(courses[: int(request.query_params.get("limit", 10))], many=True, context={"request": request})
        return Response(serializer.data)
