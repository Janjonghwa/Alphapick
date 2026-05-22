from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from catalog.views import CourseViewSet, FitnessSpotViewSet
from reviews.views import BookmarkAPIView, ReviewViewSet
from workouts.views import WorkoutRecordViewSet


router = DefaultRouter()
router.register("courses", CourseViewSet, basename="course")
router.register("fitness-spots", FitnessSpotViewSet, basename="fitness-spot")
router.register("reviews", ReviewViewSet, basename="review")
router.register("workout-records", WorkoutRecordViewSet, basename="workout-record")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/users/", include("accounts.user_urls")),
    path("api/recommendations/", include("recommendations.urls")),
    path("api/", include("stocks.urls")),
    path("api/bookmarks/", BookmarkAPIView.as_view(), name="bookmarks"),
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
