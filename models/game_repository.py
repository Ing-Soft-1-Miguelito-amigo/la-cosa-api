from entities import Game
from pony.orm import db_session
from typing import List


class GameRepository:

    @db_session
    def get_all_games(self) -> List[dict]:
        games = [
            game.to_dict()
            for game in Game.select()
        ]
        return games

    @db_session
    def get_game_by_id(self, game_id: int) -> Game:
        return Game[game_id].to_dict()

    @db_session
    def create_game(self, name: str, min_players: int, max_players: int,  password: str = None) -> Game:
        if not password:
            game = Game(name=name, min_players=min_players, max_players=max_players)
        else:
            game = Game(name=name, min_players=min_players, max_players=max_players, password=password)
        return game.to_dict()

    @db_session
    def end_game(self, game_id: int) -> dict:
        game = Game[game_id]
        game.state = 2
        return game.to_dict()

    @db_session
    def start_game(self, game_id: int) -> dict:
        game = Game[game_id]
        game.state = 1
        return game.to_dict()

    