from dataclasses import dataclass

import requests


@dataclass
class CollectorConfig:
    base_url: str
    api_key: str | None = None
    timeout: int = 15


class BaseCollector:
    source = "UNKNOWN"

    def __init__(self, config: CollectorConfig):
        self.config = config

    def fetch_page(self, params):
        headers = {}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        response = requests.get(self.config.base_url, params=params, headers=headers, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    def iter_records(self):
        raise NotImplementedError


class DurunubiCollector(BaseCollector):
    source = "DURUNUBI"


class VWorldTrailCollector(BaseCollector):
    source = "VWORLD"


class KakaoKeywordCollector(BaseCollector):
    source = "KAKAO"
