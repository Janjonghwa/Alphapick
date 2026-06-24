from datetime import date
from unittest.mock import patch

import pandas as pd
from django.test import SimpleTestCase

from stocks.management.commands.refresh_market_data import latest_kospi_trading_day


class LatestKospiTradingDayTests(SimpleTestCase):
    @patch("pykrx.stock.get_market_ohlcv_by_date")
    def test_uses_last_available_session_not_calendar_today(self, mocked_ohlcv):
        mocked_ohlcv.return_value = pd.DataFrame(
            {"close": [100, 101]},
            index=pd.DatetimeIndex(["2026-06-19", "2026-06-22"])
        )

        actual = latest_kospi_trading_day(today=date(2026, 6, 24))

        self.assertEqual(actual, date(2026, 6, 22))
        mocked_ohlcv.assert_called_once_with("20260614", "20260624", "005930")
