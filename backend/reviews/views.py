from django.db import IntegrityError
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Bookmark, Review
from .permissions import IsOwnerOrReadOnly
from .serializers import BookmarkSerializer, ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.select_related("user", "course", "fitness_spot").all()
        course_id = self.request.query_params.get("course")
        spot_id = self.request.query_params.get("fitness_spot")
        mine = self.request.query_params.get("mine")
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if spot_id:
            queryset = queryset.filter(fitness_spot_id=spot_id)
        if mine and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        return queryset


class BookmarkAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        bookmarks = Bookmark.objects.select_related("course__category", "fitness_spot__category").filter(user=request.user)
        serializer = BookmarkSerializer(bookmarks, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        serializer = BookmarkSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        try:
            bookmark, created = Bookmark.objects.get_or_create(user=request.user, **serializer.validated_data)
        except IntegrityError:
            return Response({"detail": "이미 북마크된 항목입니다."}, status=status.HTTP_409_CONFLICT)
        output = BookmarkSerializer(bookmark, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request):
        course = request.data.get("course") or request.query_params.get("course")
        fitness_spot = request.data.get("fitness_spot") or request.query_params.get("fitness_spot")
        queryset = Bookmark.objects.filter(user=request.user)
        if course:
            deleted, _ = queryset.filter(course_id=course).delete()
        elif fitness_spot:
            deleted, _ = queryset.filter(fitness_spot_id=fitness_spot).delete()
        else:
            return Response({"detail": "course 또는 fitness_spot을 지정해야 합니다."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"deleted": deleted}, status=status.HTTP_200_OK)
