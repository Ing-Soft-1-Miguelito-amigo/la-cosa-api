from pony.orm import *

db = Database()


class Partida(db.Entity):
    id = PrimaryKey(int, auto=True)
    min_players = Required(int)
    max_players = Required(int)
    password = Optional(str)
    state = Required(int)  # 0 = waiting, 1 = playing, 2 = finished
    play_direction = Required(bool)  # true = clockwise
    turn_owner = Optional(int)


db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)
