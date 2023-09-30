from pony.orm import ObjectNotFound
from pony.orm import db_session

from src.theThing.games.models import Game
from src.theThing.players.schemas import PlayerCreate, PlayerUpdate, PlayerBase
from .models import Player


def create_player(player_data: PlayerCreate, game_id: int):
    """
    It creates a player in the database from the
    PlayerCreate schema and returns the PlayerBase schema
    containing all the data from the player

    - If a player with the same name exists, then it cannot be created.
    - If the game does not exist, is full or started, then it cannot be created
    -> Then an exception its raised.
    """
    with db_session:
        try:
            game_to_join = Game[game_id]
        except ObjectNotFound:
            raise Exception("Game not found")
        if game_to_join.state != 0:
            raise Exception("Game already started")
        elif game_to_join.max_players == len(game_to_join.players):
            raise Exception("Game is full")
        # check if a player with the same name exists in the list
        elif any(
            player.name == player_data.name for player in game_to_join.players
        ):
            raise Exception("Player with same name exists")

        player = Player(**player_data.model_dump(), game=game_to_join)
        player.table_position = len(game_to_join.players)
        # player_created contains the ponyorm object instance of the new player
        player.flush()  # flush the changes to the database
        response = PlayerBase.model_validate(player)
    return response


def get_player(player_id: int, game_id: int):
    """
    This function returns the PlayerBase schema from its id
    containing all the data from the player
    """
    with db_session:
        player = Player.get(game=Game[game_id], id=player_id)
        if player is None:
            raise ObjectNotFound(Player, pkval=player_id)
        response = PlayerBase.model_validate(player)
    return response


def update_player(player: PlayerUpdate, game_id: int):
    """
    This function updates a player from the database
    and returns the PlayerBase schema with the updated data
    """
    with db_session:
        game = Game[game_id]
        player_to_update = Player.get(game=game, id=player.id)
        if player_to_update is None:
            raise ObjectNotFound(Player, pkval=player.id)
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
        game = Game[game_id]
        player = Player.get(game=game, id=player_id)
        if player is None:
            raise ObjectNotFound(Player, pkval=player_id)
        player.delete()
    return {"message": f"Player {player_id} deleted successfully"}
