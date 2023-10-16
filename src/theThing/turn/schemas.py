from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from src.theThing.cards.schemas import CardBase


class Turn(BaseModel):
    # This is used to return a turn
    owner: int
    played_card: Optional[CardBase] = None
    destination_player: Optional[str] = None
    response_card: Optional[CardBase] = None
    state: int

    model_config = ConfigDict(from_attributes=True)
