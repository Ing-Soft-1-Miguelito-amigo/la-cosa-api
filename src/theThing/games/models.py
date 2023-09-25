from pony.orm import Required, Optional, PrimaryKey

from src.theThing.models.db import db


class Game(db.Entity):

    """
    Represent a game
    """

    id = PrimaryKey(int, auto=True)
    name = Required(str)
    min_players = Required(int)
    max_players = Required(int)
    password = Optional(str)
    state = Required(int, default=0)  # 0 = waiting, 1 = playing, 2 = finished
    play_direction = Optional(bool)  # true = clockwise
    turn_owner = Optional(int)
