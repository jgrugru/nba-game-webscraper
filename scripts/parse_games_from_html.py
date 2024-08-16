import pandas as pd
from bs4 import BeautifulSoup
from devtools import debug
from pydantic import BaseModel


class ThunderGame(BaseModel):
    date: str
    time: str
    is_home: bool
    location: str
    opposing_team: str


list_of_games = []

with open("okc_thunder.html", "r") as f:
    contents = f.read()
    soup = BeautifulSoup(contents, "html.parser")
    home_games = soup.find_all("tr", class_="text-left")

    for game in home_games:
        date = game.find_all("td", class_="pl-2 py-2 font-bold")[0].text
        time = game.find_all("td", class_="pl-4")[0].text
        is_home_str = game.find_all("td", class_="pl-2 uppercase")[0].text
        is_home = False if is_home_str == "Away" else True
        location = game.find_all("td", class_="pl-2")[3].text
        opposing_team = game.find_all("p", class_="font-bold pl-1")[0].text

        new_game = ThunderGame(date=date, time=time, is_home=is_home, location=location, opposing_team=opposing_team)
        list_of_games.append(new_game)

    debug(list_of_games)

df = pd.DataFrame([game.model_dump() for game in list_of_games])
print(df)
