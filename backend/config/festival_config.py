"""
AetherQI Central Festival Configuration.
Single source of truth for festival name, year, date, timeline spans, and timezone.

Configured Festival Date (Lakshmi Puja 2026): 8 November 2026
Configured Timeline: T-10 days to T+10 days (21 calendar days)
Calendar Span: 29 October 2026 to 18 November 2026
Timezone: Asia/Kolkata
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, List
from zoneinfo import ZoneInfo

# Central Festival Parameters
FESTIVAL_NAME: str = "Diwali"
FESTIVAL_YEAR: int = 2026
FESTIVAL_DATE_STR: str = "2026-11-08"  # Lakshmi Puja / Main Festival Day
TIMEZONE: str = "Asia/Kolkata"

# Timeline Configuration: ±10 Days (21 Calendar Days Total)
TIMELINE_DAYS_BEFORE: int = 10
TIMELINE_DAYS_AFTER: int = 10
TOTAL_TIMELINE_DAYS: int = TIMELINE_DAYS_BEFORE + TIMELINE_DAYS_AFTER + 1  # 21 days

START_DATE_STR: str = "2026-10-29"
END_DATE_STR: str = "2026-11-18"

FESTIVAL_CONFIG: Dict[str, Any] = {
    "festival_name": FESTIVAL_NAME,
    "festival_year": FESTIVAL_YEAR,
    "festival_date": FESTIVAL_DATE_STR,
    "timezone": TIMEZONE,
    "days_before": TIMELINE_DAYS_BEFORE,
    "days_after": TIMELINE_DAYS_AFTER,
    "total_days": TOTAL_TIMELINE_DAYS,
    "start_date": START_DATE_STR,
    "end_date": END_DATE_STR
}

def get_festival_timezone() -> ZoneInfo:
    """Returns the ZoneInfo instance for the configured timezone."""
    return ZoneInfo(TIMEZONE)

def get_festival_date() -> datetime:
    """
    Returns the configured festival date as a timezone-aware datetime
    set to midnight in the configured timezone (Asia/Kolkata).
    """
    dt = datetime.strptime(FESTIVAL_DATE_STR, "%Y-%m-%d")
    return dt.replace(tzinfo=get_festival_timezone())

def get_timeline_date_range() -> tuple[datetime, datetime]:
    """
    Returns (start_datetime, end_datetime) representing the full 21-day window.
    """
    f_date = get_festival_date()
    start_dt = f_date - timedelta(days=TIMELINE_DAYS_BEFORE)
    end_dt = f_date + timedelta(days=TIMELINE_DAYS_AFTER)
    return start_dt, end_dt

def get_timeline_calendar_days() -> List[Dict[str, Any]]:
    """
    Generates a structured list of all 21 calendar days (T-10 to T+10).
    Includes day_offset, date string (YYYY-MM-DD), formatted display label,
    phase classification ("before_diwali", "diwali", "after_diwali"),
    and human-readable phase description.
    """
    f_date = get_festival_date()
    calendar_days = []

    for offset in range(-TIMELINE_DAYS_BEFORE, TIMELINE_DAYS_AFTER + 1):
        target_dt = f_date + timedelta(days=offset)
        date_str = target_dt.strftime("%Y-%m-%d")
        display_date = target_dt.strftime("%d %b %Y")  # e.g., "08 Nov 2026"
        short_date = target_dt.strftime("%d %b")       # e.g., "08 Nov"

        if offset < 0:
            phase = "before_diwali"
            if offset == -1:
                phase_title = "Pre-Diwali Eve (Choti Diwali)"
            elif offset in (-2, -3):
                phase_title = f"Dhanteras & Market Buildup (T{offset:+d})"
            elif offset in (-7, -6):
                phase_title = f"Early Festival Preparation (T{offset:+d})"
            else:
                phase_title = f"Pre-Diwali Baseline (T{offset:+d})"
        elif offset == 0:
            phase = "diwali"
            phase_title = "Diwali Night Peak (Lakshmi Puja)"
        else:
            phase = "after_diwali"
            if offset == 1:
                phase_title = "Post-Diwali Smog Stagnation (T+1)"
            elif offset in (2, 3):
                phase_title = f"Govardhan / Bhai Doj Smog (T{offset:+d})"
            elif offset in (4, 5, 6, 7):
                phase_title = f"Active Wind Dispersion (T{offset:+d})"
            else:
                phase_title = f"Baseline Restabilization (T{offset:+d})"

        calendar_days.append({
            "day_offset": offset,
            "date": date_str,
            "display_date": display_date,
            "short_date": short_date,
            "phase": phase,
            "phase_title": phase_title,
            "is_diwali": (offset == 0)
        })

    return calendar_days

def get_festival_config() -> Dict[str, Any]:
    """Returns the central festival configuration dictionary."""
    cfg = dict(FESTIVAL_CONFIG)
    cfg["calendar_days"] = get_timeline_calendar_days()
    return cfg

