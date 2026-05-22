from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from catalog.models import Category, Course


class CourseAPITests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="WALKING", display_name="러닝/걷기", icon="Footprints")
        self.course = Course.objects.create(
            name="테스트 코스",
            category=self.category,
            description="테스트 설명",
            distance_km=5,
            duration_min=45,
            difficulty="EASY",
            region="서울",
            start_lat=37.5,
            start_lng=127.0,
            gpx_simplified=[[127.0, 37.5], [127.1, 37.6]],
            source="TEST",
            external_id="C-1",
            nearby_transit="2호선 테스트역",
            accessibility_sources={"nearby_transit": "카카오맵"},
        )
        self.user = get_user_model().objects.create_user(username="runner", password="password123")

    def test_course_detail_includes_accessibility_empty_state(self):
        response = self.client.get(f"/api/courses/{self.course.id}/")

        self.assertEqual(response.status_code, 200)
        items = {item["key"]: item for item in response.data["accessibility_info"]}
        self.assertEqual(items["nearby_transit"]["value"], "2호선 테스트역")
        self.assertEqual(items["nearby_transit"]["source"], "카카오맵")
        self.assertIsNone(items["nearby_parking"]["value"])
        self.assertEqual(items["nearby_parking"]["display_value"], "정보 없음")

    def test_course_filters_by_query_and_difficulty(self):
        response = self.client.get("/api/courses/", {"q": "테스트", "difficulty": "EASY"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "테스트 코스")
