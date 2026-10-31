"""
Automated unit tests for Central Festival Configuration and Timeline Math.
Verifies:
1. Diwali is configured as 8 November 2026 (2026-11-08).
2. The timeline starts on 29 October 2026.
3. The timeline ends on 18 November 2026.
4. Exactly 21 calendar days are generated.
5. T-10 corresponds to 29 October.
6. T corresponds to 8 November.
7. T+10 corresponds to 18 November.
8. Timezone is Asia/Kolkata.
9. Phase classifications (before_diwali, diwali, after_diwali).
"""

from datetime import datetime
from backend.config.festival_config import (
    FESTIVAL_NAME,
    FESTIVAL_YEAR,
    FESTIVAL_DATE_STR,
    TIMEZONE,
    TIMELINE_DAYS_BEFORE,
    TIMELINE_DAYS_AFTER,
    TOTAL_TIMELINE_DAYS,
    START_DATE_STR,
    END_DATE_STR,
    get_festival_date,
    get_festival_timezone,
    get_timeline_date_range,
    get_timeline_calendar_days,
    get_festival_config
)

def test_festival_constants():
    assert FESTIVAL_NAME == "Diwali"
    assert FESTIVAL_YEAR == 2026
    assert FESTIVAL_DATE_STR == "2026-11-08"
    assert TIMEZONE == "Asia/Kolkata"
    assert TIMELINE_DAYS_BEFORE == 10
    assert TIMELINE_DAYS_AFTER == 10
    assert TOTAL_TIMELINE_DAYS == 21
    assert START_DATE_STR == "2026-10-29"
    assert END_DATE_STR == "2026-11-18"

def test_festival_timezone_and_date():
    tz = get_festival_timezone()
    assert tz.key == "Asia/Kolkata"
    
    dt = get_festival_date()
    assert dt.year == 2026
    assert dt.month == 11
    assert dt.day == 8
    assert dt.tzinfo.key == "Asia/Kolkata"

def test_timeline_date_range():
    start_dt, end_dt = get_timeline_date_range()
    assert start_dt.strftime("%Y-%m-%d") == "2026-10-29"
    assert end_dt.strftime("%Y-%m-%d") == "2026-11-18"
    # Exactly 20 days difference between start and end (21 inclusive calendar days)
    assert (end_dt.date() - start_dt.date()).days == 20

def test_timeline_calendar_days():
    days = get_timeline_calendar_days()
    assert len(days) == 21

    # Check start (T-10)
    assert days[0]["day_offset"] == -10
    assert days[0]["date"] == "2026-10-29"
    assert days[0]["phase"] == "before_diwali"
    assert days[0]["is_diwali"] is False

    # Check Diwali (T0)
    assert days[10]["day_offset"] == 0
    assert days[10]["date"] == "2026-11-08"
    assert days[10]["phase"] == "diwali"
    assert days[10]["is_diwali"] is True

    # Check end (T+10)
    assert days[20]["day_offset"] == 10
    assert days[20]["date"] == "2026-11-18"
    assert days[20]["phase"] == "after_diwali"
    assert days[20]["is_diwali"] is False

    # Check continuous sequential offsets
    for i in range(21):
        expected_offset = i - 10
        assert days[i]["day_offset"] == expected_offset

def test_get_festival_config_structure():
    cfg = get_festival_config()
    assert cfg["festival_name"] == "Diwali"
    assert cfg["festival_year"] == 2026
    assert cfg["festival_date"] == "2026-11-08"
    assert cfg["timezone"] == "Asia/Kolkata"
    assert cfg["total_days"] == 21
    assert "calendar_days" in cfg
    assert len(cfg["calendar_days"]) == 21

