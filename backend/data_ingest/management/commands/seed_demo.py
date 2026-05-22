from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from catalog.models import Category, Course, FitnessSpot


class Command(BaseCommand):
    help = "Seed demo data for OUTFIT MVP."

    def handle(self, *args, **options):
        categories = {
            "WALKING": Category.objects.update_or_create(
                name="WALKING", defaults={"display_name": "러닝/걷기", "icon": "Footprints"}
            )[0],
            "CYCLING": Category.objects.update_or_create(
                name="CYCLING", defaults={"display_name": "자전거", "icon": "Bike"}
            )[0],
            "HIKING": Category.objects.update_or_create(
                name="HIKING", defaults={"display_name": "등산", "icon": "Mountain"}
            )[0],
            "FITNESS_SPOT": Category.objects.update_or_create(
                name="FITNESS_SPOT", defaults={"display_name": "야외 운동시설", "icon": "Dumbbell"}
            )[0],
        }

        courses = [
            {
                "category": categories["WALKING"],
                "name": "서울숲 한강 러닝 코스",
                "description": "서울숲에서 한강변으로 이어지는 초보자 친화 러닝 코스입니다.",
                "distance_km": 5.2,
                "duration_min": 45,
                "difficulty": "EASY",
                "region": "서울 성동구",
                "start_lat": 37.5446,
                "start_lng": 127.0374,
                "gpx_simplified": [[127.0374, 37.5446], [127.0448, 37.5393], [127.0552, 37.5359], [127.063, 37.5315]],
                "source": "DURUNUBI",
                "external_id": "DNWW-SEOULFOREST-001",
                "nearby_parking": "서울숲 공영주차장",
                "nearby_transit": "수인분당선 서울숲역 3번 출구",
                "traveler_info": "평탄한 산책로와 한강변 구간이 이어져 초보 러너에게 적합합니다.",
                "toilet_info": "서울숲 방문자센터 및 한강공원 화장실 이용 가능",
                "convenience_info": "편의점, 음수대, 벤치가 코스 주변에 있습니다.",
                "accessibility_sources": {
                    "nearby_parking": "카카오맵",
                    "nearby_transit": "두루누비",
                    "traveler_info": "두루누비",
                    "toilet_info": "공공데이터포털",
                    "convenience_info": "두루누비",
                },
            },
            {
                "category": categories["WALKING"],
                "name": "석촌호수 순환 걷기 코스",
                "description": "호수 둘레를 따라 걷는 야간 산책 인기 코스입니다.",
                "distance_km": 2.5,
                "duration_min": 35,
                "difficulty": "EASY",
                "region": "서울 송파구",
                "start_lat": 37.5111,
                "start_lng": 127.0982,
                "gpx_simplified": [[127.0982, 37.5111], [127.1034, 37.5102], [127.1055, 37.5077], [127.1003, 37.5063]],
                "source": "DURUNUBI",
                "external_id": "DNWW-SEOKCHON-001",
                "nearby_parking": None,
                "nearby_transit": "2호선 잠실역 2번 출구",
                "traveler_info": "야간 조명이 밝고 휴식 공간이 많습니다.",
                "toilet_info": None,
                "convenience_info": "카페와 편의점이 인접합니다.",
                "accessibility_sources": {
                    "nearby_transit": "카카오맵",
                    "traveler_info": "두루누비",
                    "convenience_info": "두루누비",
                },
            },
            {
                "category": categories["HIKING"],
                "name": "북한산 둘레길 초입 코스",
                "description": "가벼운 등산 입문자를 위한 북한산 둘레길 구간입니다.",
                "distance_km": 4.8,
                "duration_min": 90,
                "difficulty": "MEDIUM",
                "region": "서울 강북구",
                "start_lat": 37.6588,
                "start_lng": 127.011,
                "gpx_simplified": [[127.011, 37.6588], [127.0168, 37.6632], [127.0202, 37.6675], [127.0243, 37.6711]],
                "source": "VWORLD",
                "external_id": "VW-BUKHANSAN-001",
                "nearby_parking": "북한산우이역 공영주차장",
                "nearby_transit": "우이신설선 북한산우이역",
                "traveler_info": "초반 경사가 있으나 표지판이 잘 정비되어 있습니다.",
                "toilet_info": "탐방지원센터 인근 화장실",
                "convenience_info": "탐방지원센터, 식수대",
                "accessibility_sources": {
                    "nearby_parking": "카카오맵",
                    "nearby_transit": "카카오맵",
                    "traveler_info": "VWorld",
                    "toilet_info": "공공데이터포털",
                    "convenience_info": "VWorld",
                },
            },
            {
                "category": categories["HIKING"],
                "name": "아차산 능선 전망 코스",
                "description": "한강 전망이 좋은 짧은 등산 코스입니다.",
                "distance_km": 3.9,
                "duration_min": 80,
                "difficulty": "MEDIUM",
                "region": "서울 광진구",
                "start_lat": 37.5528,
                "start_lng": 127.1035,
                "gpx_simplified": [[127.1035, 37.5528], [127.1068, 37.5561], [127.1114, 37.5589], [127.1168, 37.5608]],
                "source": "VWORLD",
                "external_id": "VW-ACHASAN-001",
                "nearby_parking": "아차산생태공원 주차장",
                "nearby_transit": "5호선 아차산역 2번 출구",
                "traveler_info": "전망 구간은 바람이 강할 수 있어 보온이 필요합니다.",
                "toilet_info": "생태공원 입구 화장실",
                "convenience_info": None,
                "accessibility_sources": {
                    "nearby_parking": "카카오맵",
                    "nearby_transit": "카카오맵",
                    "traveler_info": "VWorld",
                    "toilet_info": "공공데이터포털",
                },
            },
            {
                "category": categories["CYCLING"],
                "name": "한강 잠원 자전거 코스",
                "description": "평탄한 한강 자전거길로 왕복 라이딩에 좋습니다.",
                "distance_km": 12.4,
                "duration_min": 60,
                "difficulty": "EASY",
                "region": "서울 서초구",
                "start_lat": 37.5201,
                "start_lng": 127.0122,
                "gpx_simplified": [[127.0122, 37.5201], [127.0254, 37.5186], [127.0438, 37.5162], [127.0598, 37.5144]],
                "source": "DNBW",
                "external_id": "DNBW-JAMWON-001",
                "nearby_parking": "잠원한강공원 주차장",
                "nearby_transit": "3호선 잠원역 도보 이동",
                "traveler_info": None,
                "toilet_info": "한강공원 화장실",
                "convenience_info": "자전거 대여소, 편의점",
                "accessibility_sources": {
                    "nearby_parking": "카카오맵",
                    "nearby_transit": "카카오맵",
                    "toilet_info": "공공데이터포털",
                    "convenience_info": "두루누비",
                },
            },
            {
                "category": categories["WALKING"],
                "name": "경의선숲길 회복 걷기 코스",
                "description": "도심 속 녹지 축을 따라 걷는 회복형 코스입니다.",
                "distance_km": 5.0,
                "duration_min": 55,
                "difficulty": "EASY",
                "region": "서울 마포구",
                "start_lat": 37.5576,
                "start_lng": 126.9244,
                "gpx_simplified": [[126.9244, 37.5576], [126.9291, 37.5552], [126.9342, 37.5528], [126.9418, 37.5509]],
                "source": "DURUNUBI",
                "external_id": "DNWW-GYEONGUI-001",
                "nearby_parking": None,
                "nearby_transit": "공항철도 홍대입구역",
                "traveler_info": "카페와 휴식 공간이 이어지는 도심 산책로입니다.",
                "toilet_info": None,
                "convenience_info": "카페, 편의점, 벤치",
                "accessibility_sources": {
                    "nearby_transit": "카카오맵",
                    "traveler_info": "두루누비",
                    "convenience_info": "두루누비",
                },
            },
        ]

        for data in courses:
            Course.objects.update_or_create(
                source=data["source"],
                external_id=data["external_id"],
                defaults=data,
            )

        spots = [
            {
                "name": "서울숲 야외운동장",
                "category": categories["FITNESS_SPOT"],
                "equipment_types": ["철봉", "평행봉", "벤치"],
                "lat": 37.5432,
                "lng": 127.0389,
                "address": "서울 성동구 성수동1가",
                "description": "러닝 후 보강 운동을 하기 좋은 야외 운동시설입니다.",
                "source": "PUBLIC_DATA",
                "external_id": "SPOT-SEOULFOREST-001",
            },
            {
                "name": "잠실한강공원 체력단련장",
                "category": categories["FITNESS_SPOT"],
                "equipment_types": ["철봉", "윗몸일으키기", "스트레칭"],
                "lat": 37.5174,
                "lng": 127.0861,
                "address": "서울 송파구 한가람로",
                "description": "한강변 접근성이 좋은 체력단련장입니다.",
                "source": "PUBLIC_DATA",
                "external_id": "SPOT-JAMSIL-001",
            },
            {
                "name": "아차산 생태공원 운동시설",
                "category": categories["FITNESS_SPOT"],
                "equipment_types": ["철봉", "하체운동기구", "허리돌리기"],
                "lat": 37.5508,
                "lng": 127.1006,
                "address": "서울 광진구 광장동",
                "description": "등산 전후 가볍게 몸을 풀 수 있는 시설입니다.",
                "source": "PUBLIC_DATA",
                "external_id": "SPOT-ACHASAN-001",
            },
        ]

        for data in spots:
            FitnessSpot.objects.update_or_create(
                source=data["source"],
                external_id=data["external_id"],
                defaults=data,
            )

        User = get_user_model()
        user, created = User.objects.get_or_create(username="demo", defaults={"email": "demo@example.com", "nickname": "데모러너"})
        if created:
            user.set_password("demo12345")
        user.level = "EASY"
        user.preferred_location = "서울"
        user.preferred_categories = ["WALKING", "HIKING"]
        user.onboarding_completed = True
        user.save()

        self.stdout.write(self.style.SUCCESS("Seeded OUTFIT demo data. Login: demo / demo12345"))
