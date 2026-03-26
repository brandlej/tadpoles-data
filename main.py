from auth import get_session
import sys
import argparse
from argparse import Namespace
from requests import Session
from datetime import datetime
from dates import get_month_ranges_between, get_next_month
from graph import plot_hours


BASE_URL = "https://www.tadpoles.com"
EVENTS_QUERY_ENDPOINT = "/remote/v2/events/query"


def main():
    args = bootstrap_flags()
    year, month = validate_args(args)
    # (year, month) / hours napped
    hours_napped_by_month: dict[tuple[int, int], float] = {}

    ranges = get_month_ranges_between(datetime(year, month, 1), datetime(2026, 11, 1))

    session = get_session()

    for y, m in ranges:
        data = query_events_for_month(session, m, y)
        nap_entries = get_unique_nap_entries(data["payload"]["events"])
        hours_napped_by_month[(y, m)] = calc_hours_napped(nap_entries)

    plot_hours(hours_napped_by_month)


def bootstrap_flags():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m", "--month", type=int, required=True, help="Start month (1–12)"
    )
    parser.add_argument("-y", "--year", type=int, required=True, help="Start year")

    return parser.parse_args()


def validate_args(args: Namespace) -> tuple[int, int]:
    # argparse already validates type
    month = args.month
    year = args.year

    if not 1 <= month <= 12:
        sys.exit("Month must be between 1 and 12")

    if year > datetime.now().year:
        sys.exit(f"Year must be <= {datetime.now().year}")

    return year, month


def query_events_for_month(session: Session, month: int, year: int):
    next_year, next_month_value = get_next_month(year, month)

    body: dict[str, str | int] = {
        "direction": "range",
        "event_timestamp": int(datetime(year, month, 1).timestamp() * 1000),
        "end_event_timestamp": int(
            datetime(next_year, next_month_value, 1).timestamp() * 1000
        ),
        "num_events": 300,
        "client": "dashboard",
    }

    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"{BASE_URL}/home_or_work",
        "Origin": BASE_URL,
    }

    # Tadpoles looks like it uses cursor based pagination
    # To harden: Need to loop through pages and concat togather
    # Inspecting payloads in UI, it uses 300 as the item size which seems to grab all events
    response = session.post(
        f"{BASE_URL}/{EVENTS_QUERY_ENDPOINT}",
        json=body,
        headers=headers,
    )

    if not response.ok:
        raise RuntimeError("Something went wrong")

    return response.json()


def get_unique_nap_entries(events):
    daily_reports = [event for event in events if event["type"] == "DailyReport"]
    nap_entries = [
        entry
        for report in daily_reports
        for entry in report["entries"]
        if entry["type_name"] == "nap"
    ]

    seen_ids: set[str] = set()
    unique_nap_entries = []
    # probably a more pythonic was to do below with list comprehension
    for entry in nap_entries:
        if not entry["start_time"] or not entry["end_time"]:
            continue
        if entry["id"] in seen_ids:
            continue

        seen_ids.add(entry["id"])
        unique_nap_entries.append(entry)

    return unique_nap_entries


def calc_hours_napped(nap_entries):
    seconds_napped = 0
    for entry in nap_entries:
        seconds_napped += entry["end_time"] - entry["start_time"]

    return seconds_napped / 3600


if __name__ == "__main__":
    main()
