from datetime import datetime
import matplotlib.pyplot as plt


def plot_hours(hours_napped_by_month: dict[tuple[int, int], float]):
    filtered = {
        (year, month): hours
        for (year, month), hours in hours_napped_by_month.items()
        if hours > 0
    }

    # sort chronologically
    # python will compare underlying data types of type (year - int, month - int) lexicographically
    #
    # {
    #     (2024, 12): ...,
    #     (2025, 1): ...,
    #     (2024, 10): ...
    # } becomes ->
    # [
    #     ((2024, 10), ...),
    #     ((2024, 12), ...),
    #     ((2025, 1), ...)
    # ]

    sorted_items = sorted(filtered.items())
    x_labels = [
        datetime(year, month, 1).strftime("%b %y") for (year, month), _ in sorted_items
    ]
    y_values = [hours for _, hours in sorted_items]

    plt.figure(figsize=(10, 5))
    plt.plot(x_labels, y_values, marker="o")

    plt.title("Monthly Nap Hours")
    plt.xlabel("Month")
    plt.ylabel("Hours Napped")

    plt.grid(True)
    plt.tight_layout()

    plt.savefig("nap_hours.png")
