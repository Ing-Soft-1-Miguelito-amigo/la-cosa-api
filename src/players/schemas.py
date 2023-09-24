from pydantic import BaseModel, ConfigDict
from typing import Optional


class PlayerCreate(BaseModel):
    # This is used to create a player
    name: str
    owner: bool
    model_config = ConfigDict(from_attributes=True)


class PlayerBase(PlayerCreate):
    # This is used to return a player
    id: int
    table_position: Optional[int] = None
    role: Optional[int] = None
    alive: Optional[bool] = None
    quarantine: Optional[bool] = None
    owner: Optional[bool] = None


class PlayerUpdate(BaseModel):
    # This is used to update a player
    id: int
    table_position: Optional[int] = None
    role: Optional[int] = None
    alive: Optional[bool] = None
    quarantine: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)
