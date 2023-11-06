from src.theThing.models.db import db
from pony.orm import Required, Optional, PrimaryKey, composite_key, Set
from src.theThing.cards.models import Card


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    table_position = Optional(int)
    role = Optional(int)  # enum(humano,infectado,laCosa)
    alive = Optional(bool, default=True)
    quarantine = Optional(int, default=0) # amount of turns remaining in quarantine (0 means no quarantine)
    game = Required("Game", reverse="players")
    owner = Required(bool, default=False)
    hand = Set(Card, reverse="player")

    composite_key(id, game)
