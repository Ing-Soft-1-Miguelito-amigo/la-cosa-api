from pydantic import BaseModel, ConfigDict


class CardCreate(BaseModel):
    code: str
    name: str
    kind: int
    description: str
    number_in_card: int
    state: int
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
