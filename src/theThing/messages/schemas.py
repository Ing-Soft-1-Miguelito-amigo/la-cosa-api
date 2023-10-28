from pydantic import BaseModel, ConfigDict


class MessageCreate(BaseModel):
    """
    This class is used to create a message
    """
    content: str
    sender: int

    model_config = ConfigDict(from_attributes=True)


class MessageOut(MessageCreate):
    """
    This class is used to return a message
    """
    date: str
