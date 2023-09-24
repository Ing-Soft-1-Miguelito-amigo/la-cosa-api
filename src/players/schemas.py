from pydantic import BaseModel, ConfigDict


class PlayerCreate(BaseModel):
    # This is used to create a player
    name: str

    model_config = ConfigDict(from_attributes=True)
