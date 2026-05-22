from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from catalog.models import Category, Course, FitnessSpot


class ReviewAndBookmarkTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="runner", password="password123")
        self.category = Category.objects.create(name="WALKING", display_name="러닝/걷기")
        self.spot_category = Category.objects.create(name="FITNESS_SPOT", display_name="야외 운동시설")
        self.course = Course.objects.create(
            name="테스트 코스",
            category=self.category,
            distance_km=5,
            duration_min=40,
            difficulty="EASY",
            region="서울",
            start_lat=37.5,
            start_lng=127.0,
            source="TEST",
            external_id="C-1",
        )
        self.spot = FitnessSpot.objects.create(
            name="테스트 시설",
            category=self.spot_category,
            lat=37.5,
            lng=127.0,
            source="TEST",
            external_id="S-1",
        )
        self.client.force_authenticate(self.user)

    def test_review_requires_exactly_one_target(self):
        response = self.client.post(
            "/api/reviews/",
            {"course": self.course.id, "fitness_spot": self.spot.id, "rating": 5, "content": "좋아요"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_review_updates_course_rating_cache(self):
        response = self.client.post(
            "/api/reviews/",
            {"course": self.course.id, "rating": 4, "content": "달리기 좋아요"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.course.refresh_from_db()
        self.assertEqual(self.course.avg_rating, 4)
        self.assertEqual(self.course.review_count, 1)

    def test_bookmark_create_and_delete(self):
        create_response = self.client.post("/api/bookmarks/", {"course": self.course.id}, format="json")
        delete_response = self.client.delete("/api/bookmarks/", {"course": self.course.id}, format="json")

        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(delete_response.data["deleted"], 1)
