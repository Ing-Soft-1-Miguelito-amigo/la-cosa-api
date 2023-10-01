from pony.orm import Required, Optional, PrimaryKey
from src.theThing.games.models import Game
from src.theThing.players.models import Player

from src.theThing.models.db import db


class Card(db.Entity):
    id = PrimaryKey(int, auto=True)
    code = Required(str)
    name = Required(str)
    kind = Required(int)  # 0 = action, 1 = defense, 2 = obstacle, 3 = infection
    description = Required(str)
    number_in_card = Required(int)
    state = Required(
        int, default=2, unsigned=True
    )  # 0 = played, 1 = in player hand, 2 = not played (in deck)
    playable = Required(bool)
    game = Required(Game)
    player = Optional(Player)

    def before_insert(self):
        self.state = 2
        self.playable = True
        # check if the player belongs to the game
        if self.player not in self.game.players:
            raise ValueError("The player does not belong to the game")
