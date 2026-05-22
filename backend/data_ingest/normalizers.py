import re


def normalize_difficulty(value):
    text = str(value or "").strip().lower()
    if any(token in text for token in ("상", "hard", "difficult", "고급")):
        return "HARD"
    if any(token in text for token in ("중", "medium", "보통", "intermediate")):
        return "MEDIUM"
    return "EASY"


def normalize_distance_km(value, unit="km"):
    if value in (None, ""):
        return 0
    number = float(str(value).replace(",", ""))
    if unit.lower() in {"m", "meter", "meters"}:
        return round(number / 1000, 2)
    return round(number, 2)


def normalize_duration_min(value):
    if value in (None, ""):
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value)
    hours = re.search(r"(\d+)\s*(시간|h|hr)", text, re.I)
    minutes = re.search(r"(\d+)\s*(분|m|min)", text, re.I)
    total = 0
    if hours:
        total += int(hours.group(1)) * 60
    if minutes:
        total += int(minutes.group(1))
    if total:
        return total
    digits = re.findall(r"\d+", text)
    return int(digits[0]) if digits else 0


def parse_linestring(value):
    text = str(value or "").strip()
    text = text.removeprefix("LINESTRING").strip().strip("()")
    points = []
    for part in text.split(","):
        values = part.strip().split()
        if len(values) >= 2:
            lng, lat = float(values[0]), float(values[1])
            points.append([lng, lat])
    return points


def simplify_points(points, max_points=300):
    if len(points) <= max_points:
        return points
    step = max(1, len(points) // (max_points - 1))
    simplified = points[::step][: max_points - 1]
    if simplified[-1] != points[-1]:
        simplified.append(points[-1])
    return simplified
