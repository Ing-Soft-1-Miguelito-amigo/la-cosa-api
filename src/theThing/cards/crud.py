from .schemas import CardCreate, CardBase, CardUpdate
from .models import Card
from src.theThing.games.models import Game
from src.theThing.players.models import Player
from pony.orm import db_session, ObjectNotFound, select


def create_card(card: CardCreate, game_id: int):
    """
    It creates a card in the database from the
    CardCreate schema and returns the CardBase schema
    containing all the data from the card.

    Also, it adds the card to the game deck.

    If the game does not exist, then it cannot be created.
    """
    with db_session:
        try:
            game = Game[game_id]
        except ObjectNotFound:
            raise Exception("Game not found")

        card = Card(
            code=card.code,
            name=card.name,
            kind=card.kind,
            description=card.description,
            number_in_card=card.number_in_card,
            playable=card.playable,
            game=game,
        )

        card.flush()
        response = CardBase.model_validate(card)
    return response


def get_card(card_id: int, game_id: int):
    """
    This function returns the CardBase schema from its id
    containing all the data from the card
    """
    with db_session:
        card = Card.get(game=Game[game_id], id=card_id)
        if card is None:
            raise ObjectNotFound(Card, pkval=card_id)
        response = CardBase.model_validate(card)
    return response


def delete_card(card_id: int, game_id: int):
    """
    This function deletes the card from the database
    """
    with db_session:
        card = Card.get(game=Game[game_id], id=card_id)
        if card is None:
            raise ObjectNotFound(Card, pkval=card_id)
        card.delete()
    return {"message": f"Card {card_id} deleted successfully from game {game_id}"}


def give_card_to_player(card_id: int, player_id: int, game_id: int):
    """
    This function gives a card to a player
    """
    with db_session:
        card = Card.get(game=Game[game_id], id=card_id)
        if card is None:
            raise ObjectNotFound(Card, pkval=card_id)
        player = Player.get(game=Game[game_id], id=player_id)
        if player is None:
            raise ObjectNotFound(Player, pkval=player_id)
        card.player = player
        card.state = 1
        card.flush()
        response = CardBase.model_validate(card)
    return response


def update_card(card_to_update: CardUpdate, game_id: int):
    """
    This function updates the card state
    """
    with db_session:
        card = Card.get(game=Game[game_id], id=card_to_update.id)
        if card is None:
            raise ObjectNotFound(Card, pkval=card_to_update.id)
        card.state = card_to_update.state
        card.flush()
        response = CardBase.model_validate(card)
    return response
