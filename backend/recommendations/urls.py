from django.urls import path

from .views import NearbyRecommendationView, PersonalizedRecommendationView


urlpatterns = [
    path("personalized/", PersonalizedRecommendationView.as_view(), name="recommendations-personalized"),
    path("nearby/", NearbyRecommendationView.as_view(), name="recommendations-nearby"),
]
