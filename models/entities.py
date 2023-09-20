from pony.orm import *

db = Database()


class Game(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    min_players = Required(int)
    max_players = Required(int)
    password = Optional(str)
    state = Required(int, default=0)  # 0 = waiting, 1 = playing, 2 = finished
    play_direction = Optional(bool)  # true = clockwise
    turn_owner = Optional(int)


db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)
