from auth import get_session
import json
import sys


def main():
    session = get_session()

    # sample request body
    body: dict[str, str | int] = {
        "direction": "range",
        "event_timestamp": 1758517200000,  # Sep 22, 2025 00:00 MDT
        "end_event_timestamp": 1758690000000,  # Sep 24, 2025 00:00 MDT
        "num_events": 300,
        "client": "dashboard",
    }

    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.tadpoles.com/home_or_work",
        "Origin": "https://www.tadpoles.com",
    }

    response = session.post(
        "https://www.tadpoles.com/remote/v2/events/query", json=body, headers=headers
    )

    if not response.ok:
        sys.exit("Something went wrong")

    # tadpoles looks like it uses cursor based pagination
    # will need to loop through pages
    data = response.json()
    print(json.dumps(data, separators=(",", ":"), indent=4))

    # pseudo code
    # fetch pages of data for each month range (sep <> oct, oct <> nov, and so on)...could use tuples? don't really want to use static data
    # check if pagination cursor exists in response, if it does, keep fetching and append data

    # filter events for "type_name" == "nap"

    # append to dict where key = month, value = minutes napped

    # plot line chart where y = minutes napped
    # x = month starting in sept to apr


if __name__ == "__main__":
    main()
