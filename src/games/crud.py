from . import schemas, models
from pony.orm import db_session


def create_game(game: schemas.GameCreate):
    """ 
    It creates a game in the database from the
    GameCreate schema and returns the GameOut schema
    containing all the data from the game except the password

    If a game with the same name exists, then it cannot be created.
    Then an exception its raised.
    """
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
    """ 
    This function returns the GameInDB schema from its id 
    containing all the data from the game including the password
    """
    with db_session:
        game = models.Game[game_id]
        response = schemas.GameInDB.model_validate(game)
    return response

def get_all_games():
    """ 
    This funtcion returns all the games in the database
    in a list of GameBase schemas 
    """
    with db_session:
        games = models.Game.select()
        result = [schemas.GameBase.model_validate(game) for game in games]
    return result


def delete_game(game_id: int):
    """ 
    This function deletes a game from the database
    and returns a message with the result
    """
    with db_session:
        game = models.Game[game_id]
        game.delete()
    return {"message": f"Game {game_id} deleted successfully"}


def get_all_games_in_db():
    """ 
    This function gets all games in the database with all their data
    """
    with db_session:
        games = models.Game.select()
        result = [schemas.GameInDB.model_validate(game) for game in games]
    return result


def update_game(game_id: int, game: schemas.GameUpdate):
    """ 
    This functions updates a game with game_id 
    with the data in the GameUpdate schema
    """
    with db_session:
        game_to_update = models.Game[game_id]
        game_to_update.set(**game.model_dump())
        response = schemas.GameInDB.model_validate(game_to_update)
    return response
