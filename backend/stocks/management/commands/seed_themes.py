import ast
import json
import re
from collections import defaultdict
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from stocks.models import Stock, StockTheme, Theme, ThemeGroup


TICKER_RE = re.compile(r'"?(\d{6}\.(?:KS|KQ))"?')

FALLBACK_GROUPS = {
    "조선·해운": ["대형 조선", "조선 기자재", "해운·물류"],
    "철강·화학": ["철강·비철", "석유화학·정밀화학"],
    "전력 인프라": ["변압기·전력기기", "전선·케이블", "원전·SMR", "신재생·ESS", "EV충전·수소모빌리티"],
    "정유·에너지": ["정유", "가스·에너지", "에너지유통·화학"],
    "콘텐츠·엔터": ["K-엔터·IP", "게임"],
    "건설·건자재": ["대형 건설", "건자재·시멘트"],
    "건설기계·중공업": ["건설기계", "중공업·플랜트"],
    "바이오 CDMO": ["CMO·CDMO", "CDMO 전문"],
    "디지털헬스·AI의료": ["의료기기·디지털헬스", "AI의료영상·진단"],
    "금융·밸류업": ["은행·금융지주", "보험", "증권·자산운용", "대형 지주사"],
    "이차전지·ESS": ["배터리 셀", "배터리 소재", "배터리 장비·리사이클", "신재생·ESS"],
    "사이버보안": ["엔드포인트·네트워크보안", "AI위협분석·제로트러스트"],
    "유틸리티·가스": ["가스·에너지", "생활인프라·환경"],
    "반도체": ["메모리·HBM", "시스템반도체", "반도체장비·소재", "AI서버기판·패키징"],
    "로봇·자동화": ["산업로봇·물류자동화", "자율주행·전장"],
    "바이오·헬스케어": ["바이오 신약", "비만치료제·GLP-1", "의료기기·디지털헬스"],
    "물류·유통": ["유통·이커머스", "종합상사·무역", "면세·여행", "해운·물류"],
    "K-소비재": ["K-푸드·음료", "K-뷰티"],
    "K-방산": ["방산 대형주", "방산 부품·전자전"],
    "우주·위성": ["위성·발사체", "드론·우주"],
    "AI 인프라": ["AI플랫폼·클라우드", "온디바이스AI", "AI서버기판·패키징"],
    "양자컴퓨팅": ["양자보안·암호", "양자센서·하드웨어"],
    "리츠·부동산": ["상장 리츠", "부동산 개발·신탁", "리조트·숙박"],
    "식품·수산": ["가공식품", "제분·사료", "수산·원양어업", "주류·음료"],
    "패션·의류": ["의류 OEM·브랜드", "가죽·잡화", "섬유·방직"],
    "제지·포장": ["골판지·포장", "제지·펄프", "플라스틱 포장재"],
    "생활소비재": ["가구·인테리어", "렌탈·생활가전", "생활용품"],
    "미디어·광고": ["광고대행", "방송·콘텐츠", "출판·교육"],
    "IT서비스": ["SI·IT서비스", "콜센터·BPO", "데이터·호스팅"],
    "농업·사료": ["사료·곡물", "비료·농약", "농산물 유통"],
    "산업소재·부품": ["고무·플라스틱 소재", "세라믹·내화물", "산업용 부품", "유리·목재"],
    "기타": ["기타"],
}

GROUP_ICONS = {
    "리츠·부동산": "🏢",
    "식품·수산": "🍽️",
    "패션·의류": "👕",
    "제지·포장": "📦",
    "생활소비재": "🏠",
    "미디어·광고": "📺",
    "IT서비스": "💻",
    "농업·사료": "🌱",
    "산업소재·부품": "🧱",
}

FALLBACK_RULES = (
    ("리츠", "리츠·부동산", "상장 리츠"),
    ("부동산투자", "리츠·부동산", "상장 리츠"),
    ("부동산 임대", "리츠·부동산", "상장 리츠"),
    ("부동산 신탁", "리츠·부동산", "부동산 개발·신탁"),
    ("부동산신탁", "리츠·부동산", "부동산 개발·신탁"),
    ("부동산개발", "리츠·부동산", "부동산 개발·신탁"),
    ("신탁업 및 집합투자업", "리츠·부동산", "상장 리츠"),
    ("인프라", "리츠·부동산", "상장 리츠"),
    ("리얼티", "리츠·부동산", "상장 리츠"),
    ("리조트", "리츠·부동산", "리조트·숙박"),
    ("숙박", "리츠·부동산", "리조트·숙박"),
    ("가구", "생활소비재", "가구·인테리어"),
    ("매트리스", "생활소비재", "가구·인테리어"),
    ("인테리어", "생활소비재", "가구·인테리어"),
    ("정수기", "생활소비재", "렌탈·생활가전"),
    ("공기청정기", "생활소비재", "렌탈·생활가전"),
    ("생활용품", "생활소비재", "생활용품"),
    ("화장지", "생활소비재", "생활용품"),
    ("미용티슈", "생활소비재", "생활용품"),
    ("문구", "생활소비재", "생활용품"),
    ("가죽", "패션·의류", "가죽·잡화"),
    ("핸드백", "패션·의류", "가죽·잡화"),
    ("모피", "패션·의류", "가죽·잡화"),
    ("의류", "패션·의류", "의류 OEM·브랜드"),
    ("봉제", "패션·의류", "의류 OEM·브랜드"),
    ("내의", "패션·의류", "의류 OEM·브랜드"),
    ("학생복", "패션·의류", "의류 OEM·브랜드"),
    ("스포츠웨어", "패션·의류", "의류 OEM·브랜드"),
    ("방적", "패션·의류", "섬유·방직"),
    ("직물", "패션·의류", "섬유·방직"),
    ("면사", "패션·의류", "섬유·방직"),
    ("제분", "식품·수산", "제분·사료"),
    ("배합사료", "식품·수산", "제분·사료"),
    ("사료", "농업·사료", "사료·곡물"),
    ("곡물", "농업·사료", "사료·곡물"),
    ("설탕", "식품·수산", "가공식품"),
    ("제당", "식품·수산", "가공식품"),
    ("빵", "식품·수산", "가공식품"),
    ("과자", "식품·수산", "가공식품"),
    ("간장", "식품·수산", "가공식품"),
    ("휘핑크림", "식품·수산", "가공식품"),
    ("이스트", "식품·수산", "가공식품"),
    ("홈런볼", "식품·수산", "가공식품"),
    ("맛동산", "식품·수산", "가공식품"),
    ("수산", "식품·수산", "수산·원양어업"),
    ("원양", "식품·수산", "수산·원양어업"),
    ("참치", "식품·수산", "수산·원양어업"),
    ("어묵", "식품·수산", "수산·원양어업"),
    ("주류", "식품·수산", "주류·음료"),
    ("소주", "식품·수산", "주류·음료"),
    ("음료", "식품·수산", "주류·음료"),
    ("골판지", "제지·포장", "골판지·포장"),
    ("포장", "제지·포장", "골판지·포장"),
    ("판지", "제지·포장", "제지·펄프"),
    ("펄프", "제지·포장", "제지·펄프"),
    ("제지", "제지·포장", "제지·펄프"),
    ("종이", "제지·포장", "제지·펄프"),
    ("PET 용기", "제지·포장", "플라스틱 포장재"),
    ("플라스틱제품", "산업소재·부품", "고무·플라스틱 소재"),
    ("플라스틱", "산업소재·부품", "고무·플라스틱 소재"),
    ("합성수지", "산업소재·부품", "고무·플라스틱 소재"),
    ("고무", "산업소재·부품", "고무·플라스틱 소재"),
    ("세라믹", "산업소재·부품", "세라믹·내화물"),
    ("내화", "산업소재·부품", "세라믹·내화물"),
    ("위생도기", "건설·건자재", "건자재·시멘트"),
    ("유리", "산업소재·부품", "유리·목재"),
    ("목재", "산업소재·부품", "유리·목재"),
    ("MDF", "산업소재·부품", "유리·목재"),
    ("고무벨트", "산업소재·부품", "산업용 부품"),
    ("수전금구", "산업소재·부품", "산업용 부품"),
    ("병마개", "산업소재·부품", "산업용 부품"),
    ("복사기", "산업소재·부품", "산업용 부품"),
    ("프린터", "산업소재·부품", "산업용 부품"),
    ("화공약품", "철강·화학", "석유화학·정밀화학"),
    ("컨택센터", "IT서비스", "콜센터·BPO"),
    ("콜센터", "IT서비스", "콜센터·BPO"),
    ("전화번호", "IT서비스", "콜센터·BPO"),
    ("컴퓨터 프로그래밍", "IT서비스", "SI·IT서비스"),
    ("시스템 통합", "IT서비스", "SI·IT서비스"),
    ("IT 서비스", "IT서비스", "SI·IT서비스"),
    ("SI", "IT서비스", "SI·IT서비스"),
    ("데이타", "IT서비스", "데이터·호스팅"),
    ("호스팅", "IT서비스", "데이터·호스팅"),
    ("광고", "미디어·광고", "광고대행"),
    ("방송", "미디어·광고", "방송·콘텐츠"),
    ("위성방송", "미디어·광고", "방송·콘텐츠"),
    ("영화", "미디어·광고", "방송·콘텐츠"),
    ("영상콘텐츠", "미디어·광고", "방송·콘텐츠"),
    ("스포츠중계권", "미디어·광고", "방송·콘텐츠"),
    ("출판", "미디어·광고", "출판·교육"),
    ("서적", "미디어·광고", "출판·교육"),
    ("악기", "생활소비재", "생활용품"),
    ("오디오", "생활소비재", "생활용품"),
    ("비디오", "생활소비재", "생활용품"),
    ("농약", "농업·사료", "비료·농약"),
    ("비료", "농업·사료", "비료·농약"),
    ("농산물", "농업·사료", "농산물 유통"),
    ("B2B 전자상거래", "물류·유통", "유통·이커머스"),
    ("상품 종합 도매", "물류·유통", "종합상사·무역"),
    ("상품 중개", "물류·유통", "종합상사·무역"),
    ("백화점", "물류·유통", "유통·이커머스"),
    ("홈쇼핑", "물류·유통", "유통·이커머스"),
    ("할인점", "물류·유통", "유통·이커머스"),
    ("토목설계", "건설·건자재", "대형 건설"),
    ("건축설계", "건설·건자재", "대형 건설"),
    ("종합감리", "건설·건자재", "대형 건설"),
    ("엔지니어링", "건설·건자재", "대형 건설"),
    ("지질조사", "건설·건자재", "대형 건설"),
    ("건축석", "건설·건자재", "건자재·시멘트"),
    ("석공", "건설·건자재", "건자재·시멘트"),
    ("스틱인베스트먼트", "금융·밸류업", "증권·자산운용"),
    ("인베스트먼트", "금융·밸류업", "증권·자산운용"),
    ("지주", "금융·밸류업", "대형 지주사"),
    ("홀딩스", "금융·밸류업", "대형 지주사"),
    ("조선", "조선·해운", "대형 조선"),
    ("해운", "조선·해운", "해운·물류"),
    ("철강", "철강·화학", "철강·비철"),
    ("비철", "철강·화학", "철강·비철"),
    ("화학", "철강·화학", "석유화학·정밀화학"),
    ("전기", "전력 인프라", "변압기·전력기기"),
    ("전력", "전력 인프라", "변압기·전력기기"),
    ("전선", "전력 인프라", "전선·케이블"),
    ("가스", "정유·에너지", "가스·에너지"),
    ("에너지", "정유·에너지", "에너지유통·화학"),
    ("석유", "정유·에너지", "정유"),
    ("게임", "콘텐츠·엔터", "게임"),
    ("엔터", "콘텐츠·엔터", "K-엔터·IP"),
    ("오락", "콘텐츠·엔터", "K-엔터·IP"),
    ("건설", "건설·건자재", "대형 건설"),
    ("시멘트", "건설·건자재", "건자재·시멘트"),
    ("기계", "건설기계·중공업", "건설기계"),
    ("중공업", "건설기계·중공업", "중공업·플랜트"),
    ("의약", "바이오·헬스케어", "바이오 신약"),
    ("제약", "바이오·헬스케어", "바이오 신약"),
    ("바이오", "바이오·헬스케어", "바이오 신약"),
    ("의료", "디지털헬스·AI의료", "의료기기·디지털헬스"),
    ("금융", "금융·밸류업", "은행·금융지주"),
    ("은행", "금융·밸류업", "은행·금융지주"),
    ("보험", "금융·밸류업", "보험"),
    ("증권", "금융·밸류업", "증권·자산운용"),
    ("반도체", "반도체", "반도체장비·소재"),
    ("전자부품", "반도체", "AI서버기판·패키징"),
    ("자동차", "로봇·자동화", "자율주행·전장"),
    ("로봇", "로봇·자동화", "산업로봇·물류자동화"),
    ("유통", "물류·유통", "유통·이커머스"),
    ("운송", "물류·유통", "해운·물류"),
    ("음식료", "K-소비재", "K-푸드·음료"),
    ("화장품", "K-소비재", "K-뷰티"),
    ("섬유", "K-소비재", "K-소비재"),
    ("방산", "K-방산", "방산 대형주"),
    ("우주", "우주·위성", "위성·발사체"),
    ("소프트웨어", "AI 인프라", "AI플랫폼·클라우드"),
    ("통신", "AI 인프라", "AI플랫폼·클라우드"),
)


def clean_group_name(raw_name):
    parts = raw_name.split(" ", 1)
    if len(parts) == 2 and not any(ch.isalnum() for ch in parts[0]):
        return parts[0], parts[1]
    return "", raw_name


def is_noise(line):
    return (
        not line
        or line in {":", "{", "}", "[", "]"}
        or re.fullmatch(r"\d+", line)
        or line in {"groups", "sectors"}
    )


def parse_string_list(line):
    if not line.startswith("[") or ".KS" in line or ".KQ" in line:
        return None
    try:
        return ast.literal_eval(line.replace("…", "").rstrip(","))
    except (SyntaxError, ValueError):
        return None


def parse_source(path):
    text = Path(path).read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = None
    if isinstance(data, dict):
        groups = data.get("groups") or {}
        sectors = {
            theme_name: {ticker for ticker in tickers if isinstance(ticker, str)}
            for theme_name, tickers in (data.get("sectors") or {}).items()
            if isinstance(tickers, list)
        }
        return groups, sectors

    lines = [line.strip() for line in text.splitlines()]
    groups = {}
    sectors = defaultdict(set)

    section = None
    current_group = None
    current_sector = None

    for line in lines:
        if line == "groups":
            section = "groups"
            current_group = None
            continue
        if line == "sectors":
            section = "sectors"
            current_sector = None
            continue
        if is_noise(line):
            continue

        if section == "groups":
            values = parse_string_list(line)
            if values and current_group:
                groups[current_group] = values
                continue
            if line.startswith('"') or line.startswith("[") or TICKER_RE.search(line):
                continue
            current_group = line.rstrip(":")
            groups.setdefault(current_group, [])

        if section == "sectors":
            tickers = TICKER_RE.findall(line)
            if tickers and current_sector:
                for ticker in tickers:
                    sectors[current_sector].add(ticker)
                continue
            if line.startswith('"') or line.startswith("["):
                continue
            current_sector = line.rstrip(":")
            sectors.setdefault(current_sector, set())

    return groups, sectors


def fallback_theme_for(stock):
    haystack = f"{stock.name} {stock.sector} {stock.industry} {stock.primary_theme}"
    for keyword, group_name, theme_name in FALLBACK_RULES:
        if keyword in haystack:
            if theme_name == "K-소비재":
                return "K-소비재", "K-푸드·음료"
            return group_name, theme_name
    return "기타", "기타"


class Command(BaseCommand):
    help = "국내 주식 테마 그룹과 종목-테마 매핑을 재가공해 적재합니다."

    def add_arguments(self, parser):
        parser.add_argument("--source", help="DevTools에서 복사한 국내 테마 텍스트 파일 경로")
        parser.add_argument("--clear", action="store_true", help="기존 테마/연결 데이터를 삭제한 뒤 다시 적재합니다.")

    @transaction.atomic
    def handle(self, *args, **options):
        source = options.get("source")
        source_groups = {}
        source_sectors = {}

        if source:
            if not Path(source).exists():
                raise CommandError(f"source 파일을 찾을 수 없습니다: {source}")
            source_groups, source_sectors = parse_source(source)

        if options["clear"]:
            StockTheme.objects.all().delete()
            Theme.objects.all().delete()
            ThemeGroup.objects.all().delete()

        group_to_themes = {group_name: list(theme_names) for group_name, theme_names in FALLBACK_GROUPS.items()}
        for raw_group_name, theme_names in source_groups.items():
            _icon, group_name = clean_group_name(raw_group_name)
            if theme_names:
                merged_theme_names = group_to_themes.setdefault(group_name, [])
                for theme_name in theme_names:
                    if theme_name not in merged_theme_names:
                        merged_theme_names.append(theme_name)

        theme_to_group = {}
        group_objects = {}
        theme_objects = {}
        for group_index, (group_name, theme_names) in enumerate(group_to_themes.items(), start=1):
            raw_group = next((raw for raw in source_groups if clean_group_name(raw)[1] == group_name), group_name)
            icon, cleaned_name = clean_group_name(raw_group)
            icon = icon or GROUP_ICONS.get(cleaned_name, "")
            group, _created = ThemeGroup.objects.update_or_create(
                name=cleaned_name,
                defaults={"icon": icon, "sort_order": group_index},
            )
            group_objects[cleaned_name] = group
            for theme_index, theme_name in enumerate(theme_names, start=1):
                theme, _created = Theme.objects.update_or_create(
                    group=group,
                    name=theme_name,
                    defaults={"sort_order": theme_index},
                )
                theme_objects[(cleaned_name, theme_name)] = theme
                theme_to_group.setdefault(theme_name, cleaned_name)

        source_links = 0
        fallback_links = 0
        unknown_source_tickers = 0
        stocks_by_ticker = Stock.objects.in_bulk(field_name="ticker")
        primary_seen = set()

        for theme_name, tickers in source_sectors.items():
            group_name = theme_to_group.get(theme_name, "기타")
            theme = theme_objects.get((group_name, theme_name))
            if theme is None:
                group = group_objects.get(group_name) or group_objects["기타"]
                theme, _created = Theme.objects.update_or_create(group=group, name=theme_name, defaults={"sort_order": 999})
                theme_objects[(group.name, theme_name)] = theme
                theme_to_group[theme_name] = group.name

            for ticker in sorted(tickers):
                stock = stocks_by_ticker.get(ticker)
                if not stock:
                    unknown_source_tickers += 1
                    continue
                is_primary = ticker not in primary_seen
                StockTheme.objects.update_or_create(
                    stock=stock,
                    theme=theme,
                    defaults={"is_primary": is_primary, "source": "source"},
                )
                if is_primary:
                    primary_seen.add(ticker)
                    Stock.objects.filter(ticker=ticker).update(primary_theme=theme.name)
                source_links += 1

        for stock in Stock.objects.filter(is_active=True):
            if StockTheme.objects.filter(stock=stock).exists():
                continue
            group_name, theme_name = fallback_theme_for(stock)
            group = group_objects[group_name]
            theme = theme_objects[(group.name, theme_name)]
            StockTheme.objects.update_or_create(
                stock=stock,
                theme=theme,
                defaults={"is_primary": True, "source": "fallback"},
            )
            Stock.objects.filter(ticker=stock.ticker).update(primary_theme=theme.name)
            fallback_links += 1

        mapped_stocks = Stock.objects.filter(theme_links__isnull=False).distinct().count()
        self.stdout.write(self.style.SUCCESS("테마 재가공 완료"))
        self.stdout.write(f"- 그룹: {ThemeGroup.objects.count()}개")
        self.stdout.write(f"- 2차 테마: {Theme.objects.count()}개")
        self.stdout.write(f"- 종목-테마 연결: {StockTheme.objects.count()}개")
        self.stdout.write(f"- 매핑된 종목: {mapped_stocks}/{Stock.objects.filter(is_active=True).count()}개")
        self.stdout.write(f"- 원문 기반 연결: {source_links}개")
        self.stdout.write(f"- 보정 연결: {fallback_links}개")
        self.stdout.write(f"- 원문에만 있는 미확인 티커: {unknown_source_tickers}개")
