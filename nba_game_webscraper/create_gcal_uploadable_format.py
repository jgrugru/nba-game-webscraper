from datetime import date, datetime, timedelta

import pandas as pd
from pydantic import BaseModel, Field

"""Import this file directly in gclas under settings > import"""
NBA_TEAM = "thunder"
CURRENT_YEAR = date.today().year
GAMES_FILEPATH_CSV = f"data/{NBA_TEAM}_{CURRENT_YEAR}_games.csv"
IMPORT_TO_GCAL_FILE = f"data/upload_to_gcal_{NBA_TEAM}_{CURRENT_YEAR}_games.csv"


class Event(BaseModel):
    Subject: str
    Start_Date: str
    End_Date: str
    Start_Time: str
    End_Time: str
    Location: str
    All_Day_Event: bool = Field(default=False)


def parse_date_str(inputted_str) -> datetime:
    return datetime.strptime(inputted_str, "%A, %b %d %I:%M %p %Z")


if __name__ == "__main__":
    df = pd.read_csv(GAMES_FILEPATH_CSV)
    list_of_events: list[Event] = []
    for index, row in df.iterrows():
        print(row)
        dt = parse_date_str(f"{row['day']}, {row['date']} {row['time']}")
        if dt.month < 5 and dt.month > 0:
            dt = datetime(2026, dt.month, dt.day, dt.hour, dt.minute)
        else:
            dt = datetime(2025, dt.month, dt.day, dt.hour, dt.minute)
        event = Event(
            Subject=f"Thunder v. {row['opposing_team']} @ {row['arena']}",
            Start_Date=dt.strftime("%m/%d/%Y"),
            End_Date=dt.strftime("%m/%d/%Y"),
            Start_Time=dt.strftime("%I:%M %p"),
            End_Time=(dt + timedelta(hours=1)).strftime("%I:%M %p"),
            Location=row["arena"],
        )
        list_of_events.append(event)

    df = pd.DataFrame([e.model_dump() for e in list_of_events])
    df = df.rename(
        {
            "Start_Date": "Start Date",
            "End_Date": "End Date",
            "Start_Time": "Start Time",
            "End_Time": "End Time",
            "All_Day_Event": "All Day Event",
        },
        axis=1,
    )
    df.to_csv(IMPORT_TO_GCAL_FILE, index=False)
    print(df)
