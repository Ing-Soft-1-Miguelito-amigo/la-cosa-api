from pydantic import BaseModel, ConfigDict, root_validator
from typing import Optional, List
from src.players.schemas import PlayerBase


class GameBase(BaseModel):
    # This is used to return a game before it started (it has no turn owner and play direction)
    name: str
    min_players: int
    max_players: int

    model_config = ConfigDict(from_attributes=True)


class GameCreate(GameBase):
    # This is used to create a game
    password: Optional[str] = None
    

class GameInDB(GameCreate): 
    # This is used to return a game with the password and all the attributes saved
    id: int
    state: int = 0
    play_direction: Optional[bool] = None
    turn_owner: Optional[int] = None
    

class GameOut(BaseModel): 
    # This is used to return a game without the password and the attributes saved in DB
    id: int
    name: str
    min_players: int
    max_players: int
    state: int = 0
    play_direction: Optional[bool] = None
    turn_owner: Optional[int] = None
    players: List[PlayerBase] = []

    model_config = ConfigDict(from_attributes=True)


class GameUpdate(BaseModel): 
    # This is used to update a game
    state: Optional[int] = None
    play_direction: Optional[bool] = None
    turn_owner: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)