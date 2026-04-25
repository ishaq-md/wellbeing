from __future__ import annotations

import argparse
from pathlib import Path

from wellness_manager import WellnessManager


DATA_FILE = Path(__file__).parent / "wellness_data.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Health and mental wellness manager",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a daily wellness entry")
    add_parser.add_argument("--mood", type=int, choices=range(1, 11), required=True, help="Mood rating 1-10")
    add_parser.add_argument("--sleep", type=float, default=0.0, help="Sleep hours")
    add_parser.add_argument("--exercise", type=int, default=0, help="Exercise minutes")
    add_parser.add_argument("--water", type=int, default=0, help="Water glasses")
    add_parser.add_argument("--meditation", type=int, default=0, help="Meditation minutes")
    add_parser.add_argument("--stress", type=int, choices=range(1, 11), required=True, help="Stress level 1-10")
    add_parser.add_argument("--notes", type=str, default="", help="Optional notes for today")

    subparsers.add_parser("list", help="List saved wellness entries")
    subparsers.add_parser("summary", help="Show average wellness summary")
    subparsers.add_parser("trends", help="Show wellness trends by date")
    return parser


def display_entry(entry: dict[str, object]) -> None:
    for key, value in entry.items():
        print(f"{key}: {value}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    manager = WellnessManager(DATA_FILE)

    if args.command == "add":
        entry = manager.add_entry(
            mood=args.mood,
            sleep_hours=args.sleep,
            exercise_minutes=args.exercise,
            water_glasses=args.water,
            meditation_minutes=args.meditation,
            stress_level=args.stress,
            notes=args.notes,
        )
        print("Saved wellness entry:")
        display_entry(entry.to_dict())

    elif args.command == "list":
        entries = manager.list_entries()
        if not entries:
            print("No entries found. Add one with the 'add' command.")
            return
        for entry in entries:
            print("-" * 40)
            display_entry(entry.to_dict())

    elif args.command == "summary":
        summary = manager.get_summary()
        if summary["count"] == 0:
            print("No entries yet. Add a daily entry with the 'add' command.")
            return
        print("Wellness summary:")
        for key, value in summary.items():
            print(f"{key}: {value}")

    elif args.command == "trends":
        trends = manager.get_trends()
        if not trends["mood"]:
            print("No entries yet. Add a daily entry to see trends.")
            return
        print("Wellness trends by date:")
        for metric, points in trends.items():
            print(f"\n{metric.title()}:" )
            for date, value in points:
                print(f"  {date}: {value}")


if __name__ == "__main__":
    main()
