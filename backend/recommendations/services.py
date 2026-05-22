from math import asin, cos, radians, sin, sqrt

from catalog.models import Course, FitnessSpot


EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    value = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(value))


def bounding_box(lat, lng, radius_km):
    lat_delta = radius_km / 111.0
    lng_delta = radius_km / (111.0 * max(cos(radians(lat)), 0.01))
    return lat - lat_delta, lat + lat_delta, lng - lng_delta, lng + lng_delta


def filter_courses_nearby(queryset, lat, lng, radius_km=5):
    min_lat, max_lat, min_lng, max_lng = bounding_box(lat, lng, radius_km)
    candidates = queryset.filter(start_lat__gte=min_lat, start_lat__lte=max_lat, start_lng__gte=min_lng, start_lng__lte=max_lng)
    rows = []
    for course in candidates:
        distance = haversine_km(lat, lng, course.start_lat, course.start_lng)
        if distance <= radius_km:
            course.distance_from_user_km = round(distance, 2)
            rows.append(course)
    return sorted(rows, key=lambda course: (course.distance_from_user_km, -course.avg_rating, course.name))


def filter_spots_nearby(queryset, lat, lng, radius_km=5):
    min_lat, max_lat, min_lng, max_lng = bounding_box(lat, lng, radius_km)
    candidates = queryset.filter(lat__gte=min_lat, lat__lte=max_lat, lng__gte=min_lng, lng__lte=max_lng)
    rows = []
    for spot in candidates:
        distance = haversine_km(lat, lng, spot.lat, spot.lng)
        if distance <= radius_km:
            spot.distance_from_user_km = round(distance, 2)
            rows.append(spot)
    return sorted(rows, key=lambda spot: (spot.distance_from_user_km, -spot.avg_rating, spot.name))


def personalized_courses(user, limit=10):
    queryset = Course.objects.select_related("category").all()
    if user.is_authenticated:
        categories = user.preferred_categories or []
        if categories:
            queryset = queryset.filter(category__name__in=categories)
        if user.level:
            queryset = queryset.filter(difficulty=user.level)
        if user.preferred_location:
            preferred = queryset.filter(region__icontains=user.preferred_location)
            if preferred.exists():
                queryset = preferred
    return list(queryset.order_by("-avg_rating", "-review_count", "distance_km", "name")[:limit])


def _dedupe_courses(courses, exclude_id):
    seen_external_ids = set()
    seen_names = set()
    rows = []
    for course in courses:
        if course.id == exclude_id:
            continue
        external_key = course.external_id.strip().lower() if course.external_id else None
        normalized_name = course.name.strip().lower()
        if external_key and external_key in seen_external_ids:
            continue
        if normalized_name in seen_names:
            continue
        if external_key:
            seen_external_ids.add(external_key)
        seen_names.add(normalized_name)
        rows.append(course)
    return rows


def _similarity_score(base, candidate):
    if base.distance_km:
        distance_similarity = 1 - min(abs(candidate.distance_km - base.distance_km) / max(base.distance_km * 0.3, 0.1), 1)
    else:
        distance_similarity = 1
    rating_score = min(candidate.avg_rating / 5, 1)
    review_score = min(candidate.review_count / 50, 1)
    return (distance_similarity * 0.5) + (rating_score * 0.3) + (review_score * 0.2)


def similar_courses(course, limit=5):
    low = course.distance_km * 0.7
    high = course.distance_km * 1.3
    base_queryset = Course.objects.select_related("category").filter(
        category=course.category,
        difficulty=course.difficulty,
        distance_km__gte=low,
        distance_km__lte=high,
        region=course.region,
    )
    candidates = list(base_queryset)
    fallback_used = False
    if len(_dedupe_courses(candidates, course.id)) < 3:
        fallback_used = True
        fallback = Course.objects.select_related("category").filter(category=course.category).exclude(id=course.id)
        candidates = list(candidates) + list(fallback)
    deduped = _dedupe_courses(candidates, course.id)
    ordered = sorted(deduped, key=lambda row: (_similarity_score(course, row), row.avg_rating, row.review_count), reverse=True)
    for row in ordered:
        row.similar_fallback_used = fallback_used
    return ordered[:limit]
