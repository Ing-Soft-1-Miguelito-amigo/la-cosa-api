from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from src.theThing.cards.schemas import CardBase


class PlayerCreate(BaseModel):
    # This is used to create a player
    name: str
    owner: bool = False
    model_config = ConfigDict(from_attributes=True)


class PlayerBase(PlayerCreate):
    # This is used to return a player
    id: int
    name: str
    table_position: Optional[int] = None
    role: Optional[int] = None
    alive: Optional[bool] = None
    quarantine: Optional[int] = None
    owner: Optional[bool] = None
    hand: List[CardBase] = None


class PlayerForGame(BaseModel):
    # This is used to return a player, and it's public game status
    name: str
    table_position: Optional[int] = None
    alive: Optional[bool] = None
    quarantine: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class PlayerUpdate(BaseModel):
    # This is used to update a player
    table_position: Optional[int] = None
    role: Optional[int] = None
    alive: Optional[bool] = None
    quarantine: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
