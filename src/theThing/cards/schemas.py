from pydantic import BaseModel, ConfigDict


class CardCreate(BaseModel):
    """
    This class is used to create a card
    it has no state field because a card is always created in the deck
    (state = 2 is default value)
    """
    code: str
    name: str
    kind: int
    description: str
    number_in_card: int
    playable: bool

    model_config = ConfigDict(from_attributes=True)


class CardBase(BaseModel):
    id: int
    code: str
    name: str
    kind: int
    description: str
    number_in_card: int
    state: int
    playable: bool

    model_config = ConfigDict(from_attributes=True)
