from src.models.db import db
from src.games.models import Game
from pony.orm import Required, Optional, PrimaryKey


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    table_position = Optional(int)
    role = Optional(int)  # enum(humano,infectado,laCosa)
    alive = Optional(bool)
    quarantine = Optional(bool)
    game = Required(Game, reverse='players')
    owner_of = Optional(Game, reverse='owner')
