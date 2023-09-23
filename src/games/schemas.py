from pydantic import BaseModel, ConfigDict
from typing import Optional

class GameBase(BaseModel):#This is used to return a game before it started (it has no turn owner and play direction)
    name: str
    min_players: int
    max_players: int

    model_config = ConfigDict(from_attributes=True)

class GameCreate(GameBase):#This is used to create a game
    password: Optional[str] = None
    

class GameInDB(GameCreate): #This is used to return a game with the password 
    id: int
    state: int = 0
    play_direction: Optional[bool] = None
    turn_owner: Optional[int] = None
    

class GameOut(BaseModel): #This is used to return a game without the password
    id: int
    name: str
    min_players: int
    max_players: int
    state: int = 0
    play_direction: Optional[bool] = None
    turn_owner: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class GameUpdate(BaseModel):
    state: Optional[int] = None
    play_direction: Optional[bool] = None
    turn_owner: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)