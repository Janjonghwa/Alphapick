from django.test import SimpleTestCase

from data_ingest.normalizers import normalize_difficulty, normalize_distance_km, normalize_duration_min, parse_linestring, simplify_points


class NormalizerTests(SimpleTestCase):
    def test_normalizes_units_and_difficulty(self):
        self.assertEqual(normalize_distance_km(1500, unit="m"), 1.5)
        self.assertEqual(normalize_duration_min("1시간 20분"), 80)
        self.assertEqual(normalize_difficulty("중급"), "MEDIUM")

    def test_linestring_to_geojson_coordinate_order(self):
        points = parse_linestring("LINESTRING(127.0 37.5, 127.1 37.6)")

        self.assertEqual(points, [[127.0, 37.5], [127.1, 37.6]])

    def test_simplify_preserves_endpoints(self):
        points = [[127.0 + i * 0.001, 37.0 + i * 0.001] for i in range(1000)]
        simplified = simplify_points(points, max_points=300)

        self.assertLessEqual(len(simplified), 300)
        self.assertEqual(simplified[0], points[0])
        self.assertEqual(simplified[-1], points[-1])
