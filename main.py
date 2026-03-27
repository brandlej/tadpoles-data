from auth import get_session
import sys
import argparse
from argparse import Namespace
from requests import Session
from datetime import datetime
from dates import get_month_ranges_between, get_next_month
from graph import plot_hours


BASE_URL = "https://www.tadpoles.com"
EVENTS_QUERY_ENDPOINT = "remote/v2/events/query"
HEADERS = {
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"{BASE_URL}/parents",
    "Origin": BASE_URL,
    "X-TADPOLES-DEVICE-PLATFORM": "web",
    "X-TADPOLES-APP-ID": "com.tadpoles.web.parent",
}


def main():
    args = bootstrap_flags()
    year, month = validate_args(args)
    # (year, month) / hours napped
    hours_napped_by_month: dict[tuple[int, int], float] = {}

    ranges = get_month_ranges_between(
        datetime(year, month, 1),
        datetime(datetime.now().year, datetime.now().month, 1),
    )

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
    month = args.month
    year = args.year

    if not 1 <= month <= 12:
        sys.exit("Month must be between 1 and 12")

    current_year = datetime.now().year
    if year > current_year:
        sys.exit(f"Year must be <= {current_year}")

    return year, month


def query_events_for_month(session: Session, month: int, year: int):
    next_year, next_month_value = get_next_month(year, month)

    body = {
        "direction": "range",
        "event_timestamp": int(datetime(year, month, 1).timestamp() * 1000),
        "end_event_timestamp": int(
            datetime(next_year, next_month_value, 1).timestamp() * 1000
        ),
        "num_events": 300,
        "client": "dashboard",
    }

    # Tadpoles looks like it uses cursor based pagination
    # To harden: Loop through pages and concat togather
    # Inspecting payloads in UI, it uses 300 as the item size which seems to grab all events for now
    response = session.post(
        f"{BASE_URL}/{EVENTS_QUERY_ENDPOINT}",
        json=body,
        headers=HEADERS,
    )

    if not response.ok:
        raise RuntimeError(f"Something went wrong ({response.status_code})")

    return response.json()


def get_unique_nap_entries(events):
    seen_ids = set()
    unique_nap_entries = []

    daily_reports = [event for event in events if event.get("type") == "DailyReport"]
    entries = [
        entry
        for report in daily_reports
        for entry in (report.get("entries") or report.get("legacy_entries") or [])
    ]

    for entry in entries:
        # "type" is legacy key
        entry_type = entry.get("type_name") or entry.get("type")

        if entry_type != "nap":
            continue

        start = entry.get("start_time")
        end = entry.get("end_time")

        if not start or not end:
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
