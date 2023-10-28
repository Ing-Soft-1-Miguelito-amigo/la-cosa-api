from pony.orm import Required, Set, Optional, PrimaryKey
from src.theThing.models.db import db
from src.theThing.players.models import Player
from src.theThing.cards.models import Card
from src.theThing.turn.models import Turn
from src.theThing.messages.models import Message

class Game(db.Entity):

    """
    Represent a game
    """

    id = PrimaryKey(int, auto=True)
    name = Required(str)
    min_players = Required(int)
    max_players = Required(int)
    password = Optional(str)
    state = Required(
        int, default=0
    )  # 0 = waiting, 1 = playing, 2 = finished, 3 = aborted
    play_direction = Optional(bool)  # true = clockwise
    turn = Optional(Turn, reverse="game")
    players = Set(Player, reverse="game")
    deck = Set(Card, reverse="game")
    chat = Set(Message)
