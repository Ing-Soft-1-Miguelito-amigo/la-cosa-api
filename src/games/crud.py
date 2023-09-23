from . import schemas, models
from pony.orm import db_session

def create_game(game: schemas.GameCreate):
    with db_session:
        if models.Game.exists(name=game.name):
            raise Exception("Game already exists")
        elif game.password:
            game = models.Game(name=game.name,
                                min_players=game.min_players,
                                max_players=game.max_players,
                                password=game.password)
        else:
            game = models.Game(name=game.name,
                                min_players=game.min_players,
                                max_players=game.max_players)
        game.flush()
        response = schemas.GameOut.model_validate(game)
    return response

def get_game(game_id: int):
    with db_session:
        try:
            game = models.Game[game_id]
            response = schemas.GameInDB.model_validate(game)
        except Exception as e:
            return {"message": f"Game {game_id} not found"}
    return response

def get_all_games():
    with db_session:
        games = models.Game.select()
        result = [schemas.GameBase.model_validate(game) for game in games]
    return result


def delete_game(game_id: int):
    with db_session:
        try:
            game = models.Game[game_id]
            game.delete()
        except Exception as e:
            return {"message": f"Game {game_id} not found"}
    return {"message": f"Game {game_id} deleted successfully"}

def get_all_games_in_db():
    with db_session:
        games = models.Game.select()
        result = [schemas.GameInDB.model_validate(game) for game in games]
    return result

def update_game(game_id: int, game: schemas.GameUpdate):
    with db_session:
        try:
            game_to_update = models.Game[game_id]
            game_to_update.set(**game.model_dump())
            response = schemas.GameInDB.model_validate(game_to_update)
        except Exception as e:
            return {"message": f"Game {game_id} not found"}
    return response