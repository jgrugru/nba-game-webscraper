"""Color imported Thunder games on Google Calendar: blue for home, orange for away.

Dry run by default. Pass --apply to write the changes.
"""

import os
import sys
from datetime import date, datetime

import pandas as pd
from dotenv import load_dotenv
from gcsa.google_calendar import GoogleCalendar

NBA_TEAM = "thunder"
CURRENT_YEAR = date.today().year
GAMES_FILEPATH_CSV = f"data/{NBA_TEAM}_{CURRENT_YEAR}_games.csv"
CALENDAR_NAME = "Caption OKC Thunder Games"
HOME_COLOR = "9"  # blueberry
AWAY_COLOR = "6"  # tangerine
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_calendar() -> tuple[GoogleCalendar, str]:
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
    creds = os.getenv("GCAL_CREDENTIALS_FILEPATH", "")
    if not os.path.exists(creds):
        # .env may still point at an old machine's path; the file lives in this repo's .vscode/
        creds = os.path.join(
            PROJECT_ROOT, ".vscode", os.path.basename(creds) or "credentials.json"
        )
    gc = GoogleCalendar(credentials_path=creds)
    cal_id = next(c.id for c in gc.get_calendar_list() if c.summary == CALENDAR_NAME)
    return gc, cal_id


def game_date(row: pd.Series) -> date:
    dt = datetime.strptime(f"{row['date']} {row['time']}", "%b %d %I:%M %p %Z")
    year = CURRENT_YEAR if dt.month >= 7 else CURRENT_YEAR + 1
    return date(year, dt.month, dt.day)


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    df = pd.read_csv(GAMES_FILEPATH_CSV)
    games = {
        (game_date(row), row["opposing_team"]): bool(row["is_home"])
        for _, row in df.iterrows()
    }

    gc, cal_id = get_calendar()
    season_start = datetime(min(d for d, _ in games).year, 1, 1)
    season_end = datetime(max(d for d, _ in games).year + 1, 1, 1)
    events = list(
        gc.get_events(season_start, season_end, calendar_id=cal_id, single_events=True)
    )

    matched, unmatched, changed = 0, [], 0
    for event in events:
        start = event.start.date() if isinstance(event.start, datetime) else event.start
        hit = next(
            (key for key in games if key[0] == start and key[1] in event.summary), None
        )
        if hit is None:
            unmatched.append(f"{start} {event.summary}")
            continue
        matched += 1
        is_home = games[hit]
        want = HOME_COLOR if is_home else AWAY_COLOR
        status = "ok" if event.color_id == want else "CHANGE"
        print(
            f"{status:6} {start} {'HOME' if is_home else 'AWAY'} {event.summary!r} color {event.color_id} -> {want}"
        )
        if event.color_id != want:
            changed += 1
            if apply:
                event.color_id = want
                gc.update_event(event, calendar_id=cal_id)

    print(
        f"\n{len(events)} events on calendar, {matched} matched to CSV, {changed} {'updated' if apply else 'would change'}"
    )
    if unmatched:
        print(f"{len(unmatched)} unmatched (left alone):")
        for line in unmatched:
            print("  ", line)
    if not apply:
        print("\nDry run. Re-run with --apply to write.")
