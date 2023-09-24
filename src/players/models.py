from src.models.db import db
from pony.orm import Required, Optional, PrimaryKey


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    table_position = Optional(int)
    role = Optional(int)  # enum(humano,infectado,laCosa)
    alive = Optional(bool, default=True)
    quarantine = Optional(bool, default=False)
    game = Required('Game', reverse='players')
    owner = bool
