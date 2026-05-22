from django.test import TestCase

from catalog.models import Category, Course
from recommendations.services import filter_courses_nearby, similar_courses


class RecommendationServiceTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="WALKING", display_name="러닝/걷기")
        self.base = self.make_course("한강 5K", "BASE", 5.0, "서울")
        self.same = self.make_course("한강 5K B", "A", 5.2, "서울", rating=4.5, reviews=10)
        self.duplicate_name = self.make_course("한강 5K B", "B", 5.1, "서울", rating=5, reviews=30)
        self.duplicate_external = self.make_course("다른 이름", "A", 5.3, "서울", rating=5, reviews=30, source="OTHER")
        self.fallback = self.make_course("마포 회복 코스", "F", 6.0, "서울 마포구", rating=4, reviews=5)

    def make_course(self, name, external_id, distance, region, rating=0, reviews=0, source="TEST"):
        return Course.objects.create(
            name=name,
            category=self.category,
            distance_km=distance,
            duration_min=45,
            difficulty="EASY",
            region=region,
            start_lat=37.5 + (distance / 100),
            start_lng=127.0,
            source=source,
            external_id=external_id,
            avg_rating=rating,
            review_count=reviews,
        )

    def test_similar_courses_excludes_current_and_dedupes(self):
        result = similar_courses(self.base, limit=5)
        names = [course.name for course in result]
        external_ids = [course.external_id for course in result]

        self.assertNotIn(self.base.id, [course.id for course in result])
        self.assertEqual(len(names), len(set(name.lower() for name in names)))
        self.assertEqual(len(external_ids), len(set(external_ids)))
        self.assertLessEqual(len(result), 5)

    def test_nearby_uses_radius(self):
        result = filter_courses_nearby(Course.objects.all(), 37.5, 127.0, radius_km=20)

        self.assertTrue(any(course.id == self.base.id for course in result))
