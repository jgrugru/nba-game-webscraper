import os
from datetime import date

import pandas as pd
from bs4 import BeautifulSoup
from devtools import debug
from selenium import webdriver

from nba_game_webscraper.thunder_game import ThunderGame

NBA_TEAM = "thunder"
NBA_URL = f"https://www.nba.com/{NBA_TEAM}/schedule"
CURRENT_YEAR = date.today().year
HTML_FILEPATH = f"data/{CURRENT_YEAR}_raw_html_{NBA_TEAM}.html"
GAMES_FILEPATH_CSV = f"data/{NBA_TEAM}_{CURRENT_YEAR}_games.csv"


def get_games_html() -> BeautifulSoup:
    driver = webdriver.Chrome()
    driver.get(url=NBA_URL)
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    driver.quit()
    with open(HTML_FILEPATH, "w") as file:
        file.write(str(soup))
    return soup


def get_html_from_file() -> BeautifulSoup:
    if not os.path.exists(HTML_FILEPATH):
        return get_games_html()

    with open(file=HTML_FILEPATH, mode="r") as file:
        soup = BeautifulSoup(file.read(), features="html.parser")
    return soup


if __name__ == "__main__":
    soup = get_html_from_file()
    div = list(soup.find("main").find("div").children)[2]
    uls = div.find_all("ul")

    list_of_games: list[ThunderGame] = []
    for ul in uls:
        games = ul.find_all("div", class_="my-6")

        for game in games:
            date = game.find("div", {"data-testid": "date"}).text
            is_home = False if game.find("span", {"data-testid": "schedule-item-type"}).text.lower() == "away" else True
            day = game.find("div", {"data-testid": "day"}).text
            time = game.find("div", {"data-testid": "time"}).text
            arena = game.find("div", {"data-testid": "arena-location"}).text
            team_city = game.find("p", {"data-testid": "team-city"}).text
            team_name = game.find("p", {"data-testid": "team-name"}).text
            broadcaster = "No Broadcast Listed" if game.find("span", {"data-testid": "broadcaster"}) is None else game.find("span", {"data-testid": "broadcaster"}).text

            new_game = ThunderGame(date=date, is_home=is_home, day=day, time=time, arena=arena, team_city=team_city, opposing_team=team_name, broadcaster=broadcaster)
            debug(new_game)
            list_of_games.append(new_game)

    df = pd.DataFrame([game.model_dump() for game in list_of_games])
    df.to_csv(GAMES_FILEPATH_CSV, index=False)
    print(df)
