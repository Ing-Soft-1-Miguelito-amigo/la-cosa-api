from models.entities import Game
from pydantic import BaseModel, ConfigDict


class GameBase(BaseModel):#This is used to return a game before it started (it has no turn owner and play direction)
    name: str
    min_players: int
    max_players: int

    model_config = ConfigDict(from_attributes=True)

class GameCreate(GameBase):#This is used to create a game
    password: str = None
    

class GameInDB(GameBase): #This is used to return a game with the password 
    id: int
    state: int = 0
    play_direction: bool = True
    turn_owner: int = None
    

class GameOut(BaseModel): #This is used to return a game without the password
    id: int
    name: str
    min_players: int
    max_players: int
    state: int = 0
    play_direction: None | bool 
    turn_owner: int | None
    
    model_config = ConfigDict(from_attributes=True)
