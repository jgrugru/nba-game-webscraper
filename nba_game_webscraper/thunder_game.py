from pydantic import BaseModel


class ThunderGame(BaseModel):
    date: str
    is_home: bool
    day: str
    time: str
    arena: str
    team_city: str
    opposing_team: str
    broadcaster: str
