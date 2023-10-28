from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from src.theThing.players.schemas import PlayerForGame, PlayerBase
from src.theThing.cards.schemas import CardBase
from src.theThing.turn.schemas import TurnOut
from src.theThing.messages.schemas import MessageOut


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
    turn: Optional[TurnOut] = None
    players: List[PlayerBase] = None
    deck: List[CardBase] = None
    chat: List[MessageOut] = []

    @classmethod
    def model_validate(cls, game):
        ordered_chat = game.chat.order_by(lambda x: x.date)
        formatted_chat = [
            MessageOut.model_validate(message) for message in ordered_chat
        ]
        return cls(
            id=game.id,
            name=game.name,
            min_players=game.min_players,
            max_players=game.max_players,
            password=game.password,
            state=game.state,
            play_direction=game.play_direction,
            turn=game.turn,
            players=game.players,
            deck=game.deck,
            chat=formatted_chat,
        )


class GameOut(BaseModel):
    # This is used to return a game without the password and the attributes saved in DB
    id: int
    name: str
    min_players: int
    max_players: int
    state: int = 0
    play_direction: Optional[bool] = None
    turn: Optional[TurnOut] = None
    players: List[PlayerForGame] = []
    chat: List[MessageOut] = []

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, game):
        # first order teh chat by date
        ordered_chat = game.chat.order_by(lambda x: x.date)
        formatted_chat = [
            MessageOut.model_validate(message) for message in ordered_chat
        ]
        return cls(
            id=game.id,
            name=game.name,
            min_players=game.min_players,
            max_players=game.max_players,
            state=game.state,
            play_direction=game.play_direction,
            turn=game.turn,
            players=game.players,
            chat=formatted_chat,
        )


class GamePlayerAmount(GameBase):
    # This is used to return a game with the amount of players
    # It is used in the list of games
    id: int
    amount_of_players: int

    model_config = ConfigDict(from_attributes=True)


class GameUpdate(BaseModel):
    # This is used to update a game
    state: Optional[int] = None
    play_direction: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)
