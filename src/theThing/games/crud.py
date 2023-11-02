from . import schemas, models
from pony.orm import db_session
from src.theThing.players.models import Player
from src.theThing.cards.schemas import CardCreate
from src.theThing.cards.crud import create_card
from src.theThing.cards.static_cards import dict_of_cards
from src.theThing.messages.schemas import MessageOut


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
            raise Exception("Ya existe una partida con el mismo nombre")
        elif game.password:
            game = models.Game(
                name=game.name,
                min_players=game.min_players,
                max_players=game.max_players,
                password=game.password,
            )
        else:
            game = models.Game(
                name=game.name,
                min_players=game.min_players,
                max_players=game.max_players,
            )
        game.flush()
        response = schemas.GameOut.model_validate(game)
    return response


def get_game(game_id: int):
    """
    This function returns the GameOut schema from its id
    containing all the data from the game including the password
    """
    with db_session:
        game = models.Game[game_id]
        if game.turn is not None:
            played_card = None
            response_card = None
            destination_player = ""

            if game.turn.played_card is not None:
                played_card = models.Card[game.turn.played_card]
            if game.turn.response_card is not None:
                response_card = models.Card[game.turn.response_card]
            if game.turn.destination_player is not None:
                destination_player = game.turn.destination_player
            if game.turn.destination_player_exchange is not None:
                destination_player_exchange = (
                    game.turn.destination_player_exchange
                )

            return_turn = schemas.TurnOut(
                owner=game.turn.owner,
                played_card=played_card,
                destination_player=destination_player,
                response_card=response_card,
                destination_player_exchange=destination_player_exchange,
                state=game.turn.state,
            )
            ordered_chat = game.chat.order_by(lambda x: x.date)
            return_game = schemas.GameOut(
                id=game.id,
                name=game.name,
                min_players=game.min_players,
                max_players=game.max_players,
                state=game.state,
                play_direction=game.play_direction,
                turn=return_turn,
                players=game.players,
                chat=[
                    MessageOut.model_validate(message)
                    for message in ordered_chat
                ],
            )

            response = return_game
        else:
            response = schemas.GameOut.model_validate(game)
    return response


def get_full_game(game_id: int):
    """
    This function returns the GameInDB schema from its id
    containing all the data from the game including full information of the players
    """
    with db_session:
        game = models.Game[game_id]
        if game.turn is not None:
            played_card = None
            response_card = None
            destination_player = ""

            if game.turn.played_card is not None:
                played_card = models.Card[game.turn.played_card]
            if game.turn.response_card is not None:
                response_card = models.Card[game.turn.response_card]
            if game.turn.destination_player is not None:
                destination_player = game.turn.destination_player

            return_turn = schemas.TurnOut(
                owner=game.turn.owner,
                played_card=played_card,
                destination_player=destination_player,
                response_card=response_card,
                state=game.turn.state,
            )
            ordered_chat = game.chat.order_by(lambda x: x.date)
            return_game = schemas.GameInDB(
                id=game.id,
                name=game.name,
                min_players=game.min_players,
                max_players=game.max_players,
                state=game.state,
                play_direction=game.play_direction,
                turn=return_turn,
                players=game.players,
                deck=game.deck,
                chat=[
                    MessageOut.model_validate(message)
                    for message in ordered_chat
                ],
            )
            return return_game
        else:
            response = schemas.GameInDB.model_validate(game)
    return response


def get_all_games() -> list[schemas.GameOut]:
    """
    This function returns all the games in the database
    in a list of GameOut schemas
    """
    with db_session:
        games = models.Game.select()
        result = [schemas.GameOut.model_validate(game) for game in games]
    return result


def delete_game(game_id: int):
    """
    This function deletes a game from the database
    and returns a message with the result
    """
    with db_session:
        game = models.Game[game_id]
        game.delete()
    return {"message": f"Partida {game_id} eliminada con éxito"}


def get_all_games_in_db():
    """
    This function gets all games in the database with all their data
    """
    with db_session:
        games = models.Game.select()
        result = [schemas.GameInDB.model_validate(game) for game in games]
    return result


def update_game(game_id: int, game: schemas.GameUpdate) -> schemas.GameInDB:
    """
    This functions updates a game with game_id
    with the data in the GameUpdate schema
    """
    with db_session:
        game_to_update = models.Game[game_id]
        game_to_update.set(**game.model_dump(exclude_unset=True))
        game_to_update.flush()
        if game_to_update.turn is not None:
            played_card = None
            response_card = None
            destination_player = ""

            if game_to_update.turn.played_card is not None:
                played_card = models.Card[game_to_update.turn.played_card]
            if game_to_update.turn.response_card is not None:
                response_card = models.Card[game_to_update.turn.response_card]
            if game_to_update.turn.destination_player is not None:
                destination_player = game_to_update.turn.destination_player

            return_turn = schemas.TurnOut(
                owner=game_to_update.turn.owner,
                played_card=played_card,
                destination_player=destination_player,
                response_card=response_card,
                state=game_to_update.turn.state,
            )
            ordered_chat = game_to_update.chat.order_by(lambda x: x.date)
            return_game = schemas.GameInDB(
                id=game_to_update.id,
                name=game_to_update.name,
                min_players=game_to_update.min_players,
                max_players=game_to_update.max_players,
                state=game_to_update.state,
                play_direction=game_to_update.play_direction,
                turn=return_turn,
                players=game_to_update.players,
                deck=game_to_update.deck,
                chat=[
                    MessageOut.model_validate(message)
                    for message in ordered_chat
                ],
            )
            return return_game
        else:
            response = schemas.GameInDB.model_validate(game_to_update)
    return response


def create_game_deck(game_id: int, players_amount: int):
    """
    This function creates a deck for the game
    PRE: The game exists
    """
    # Filter cards by number
    filtered_dict = {
        key: value
        for key, value in dict_of_cards.items()
        if value["number_in_card"] <= players_amount
    }

    # Create cards
    for card in filtered_dict.values():
        for _ in range(card["amount_in_deck"]):
            new_card = CardCreate(
                code=card["code"],
                name=card["name"],
                kind=card["kind"],
                description=card["description"],
                number_in_card=card["number_in_card"],
                playable=True,
            )
            create_card(new_card, game_id)
