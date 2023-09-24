from src.games import crud as games_crud
from pony.orm import db_session
from src.players.schemas import PlayerCreate, PlayerUpdate, PlayerBase


def create_player(player: PlayerCreate, game: int):
    """
    It creates a player in the database from the
    PlayerCreate schema and returns the PlayerBase schema
    containing all the data from the player

    If a player with the same name exists, then it cannot be created.
    Then an exception its raised.
    """
    with db_session:
        game_to_join = games_crud.get_game(game)
        if game_to_join.state != 0:
            raise Exception("Game already started")
        elif game_to_join.max_players == len(game_to_join.players):
            raise Exception("Game is full")
        # check if a player with the same name exists
        elif game_to_join.players.exists(name=player.name):
            raise Exception("Player with same name exists")

        player_created = game_to_join.players.create(player.model_dump())
        player_created.table_position = len(game_to_join.players)
        # player_created contains the ponyorm object instance of the new player
        player.flush()  # flush the changes to the database
        response = player_created.model_validate(player_created)
    return response


def get_player(player_id: int, game_id: int):
    """
    This function returns the PlayerBase schema from its id
    containing all the data from the player
    """
    with db_session:
        player = games_crud.get_game(game_id).players[player_id]
        response = PlayerBase.model_validate(player)
    return response


def update_player(player: PlayerUpdate, game_id: int):
    """
    This function updates a player from the database
    and returns the PlayerBase schema with the updated data
    """
    with db_session:
        player_to_update = games_crud.get_game(game_id).players[player.id]
        player_to_update.set(**player.model_dump())
        player_to_update.flush()
        response = PlayerBase.model_validate(player_to_update)
    return response


def delete_player(player_id: int, game_id: int):
    """
    This function deletes a player from the database
    and returns a message with the result
    """
    with db_session:
        player = games_crud.get_game(game_id).players[player_id]
        player.delete()
    return {"message": f"Player {player_id} deleted successfully"}
