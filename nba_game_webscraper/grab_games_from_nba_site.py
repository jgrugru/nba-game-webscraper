import json
import re
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd
import requests

from nba_game_webscraper.thunder_game import ThunderGame

NBA_TEAM = "thunder"
NBA_URL = f"https://www.nba.com/{NBA_TEAM}/schedule"
CURRENT_YEAR = date.today().year
GAMES_FILEPATH_CSV = f"data/{NBA_TEAM}_{CURRENT_YEAR}_games.csv"
LOCAL_TZ = ZoneInfo("America/Chicago")
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"


def get_schedule_json() -> list[dict]:
    """The schedule page is a Next.js app; the games are embedded in the __NEXT_DATA__ script tag."""
    html = requests.get(NBA_URL, headers={"User-Agent": USER_AGENT}, timeout=30).text
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S
    )
    data = json.loads(match.group(1))
    return data["props"]["pageProps"]["scheduleData"]["schedule"]


def broadcaster_text(broadcasters: dict, is_home: bool) -> str:
    local_key = "homeTvBroadcasters" if is_home else "awayTvBroadcasters"
    names = [
        b["broadcasterDisplay"]
        for b in broadcasters["nationalBroadcasters"] + broadcasters[local_key]
    ]
    return "/".join(names) if names else "No Broadcast Listed"


def to_thunder_game(game: dict) -> ThunderGame:
    is_home = game["homeTeam"]["teamSlug"] == NBA_TEAM
    opponent = game["awayTeam"] if is_home else game["homeTeam"]
    tip_off = datetime.fromisoformat(game["gameTimeUTC"]).astimezone(LOCAL_TZ)
    return ThunderGame(
        date=tip_off.strftime("%b %d"),
        is_home=is_home,
        day=tip_off.strftime("%A"),
        time=tip_off.strftime("%I:%M %p %Z").lstrip("0"),
        arena=f"{game['arenaCity']}, {game['arenaState']}",
        team_city=opponent["teamCity"],
        opposing_team=opponent["teamName"],
        broadcaster=broadcaster_text(game["broadcasters"], is_home),
        label=game["gameLabel"] or "Regular Season",
    )


if __name__ == "__main__":
    games = [to_thunder_game(g) for g in get_schedule_json()]
    df = pd.DataFrame([game.model_dump() for game in games])
    df.to_csv(GAMES_FILEPATH_CSV, index=False)
    print(df)
