import os

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from thunder_game import ThunderGame
from devtools import debug


NBA_TEAM = "thunder"
NBA_URL = f"https://www.nba.com/{NBA_TEAM}/schedule"
HTML_FILEPATH = f"data/raw_html_{NBA_TEAM}.html"
GAMES_FILEPATH_CSV = f"data/{NBA_TEAM}_games.csv"


def get_unordered_list_of_games(call_selenium: bool = False) -> BeautifulSoup:
    if not os.path.exists(HTML_FILEPATH) or call_selenium:
        driver = webdriver.Chrome()
        driver.get(NBA_URL)
        soup = BeautifulSoup(driver.page_source, features="html.parser")
        div = list(soup.find("main").find("div").children)[2]
        ul = div.find("ul")

        with open(HTML_FILEPATH, "w") as file:
            file.write(str(ul))
        return ul
    else:
        with open(HTML_FILEPATH, "r") as file:
            soup = BeautifulSoup(file.read(), features="html.parser")
        return soup


if __name__ == "__main__":
    list_of_games = []
    ul = get_unordered_list_of_games()
    games = ul.find_all("div", class_="my-6")

    list_of_games = []
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
    df.to_csv(GAMES_FILEPATH_CSV)
    print(df)
