import os
from datetime import datetime

import pandas as pd
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar


def parse_date_str(inputted_str):
    return datetime.strptime(inputted_str, "%a, %b %d %I:%M %p")


calendar = GoogleCalendar(
    # 'jeff.gruenbaum@gmail.com',
    default_calendar=os.getenv("DEFAULT_CALENDAR_ID"),
    credentials_path=os.getenv("GCAL_CREDENTIALS_FILEPATH"),
)

list_of_events = []
df = pd.read_csv("data/thunder_games.csv")
for index, row in df.iterrows():
    print(row)
    date = parse_date_str(row["date"] + " " + row["time"])
    if date.month < 5 and date.month > 0:
        date = datetime(2025, date.month, date.day, date.hour, date.minute)
    else:
        date = datetime(2024, date.month, date.day, date.hour, date.minute)
    # print(date)
    event = Event(f"Thunder v. {row['opposing_team']} @ {row['location']}", start=date, location=row["location"], color_id="9" if row["is_home"] else "6")
    calendar.add_event(event)
    pass
