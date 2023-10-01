from .test_setup import test_db, clear_db
from src.theThing.cards import crud as card_crud
from src.theThing.cards.schemas import CardCreate, CardBase
from src.theThing.games import crud as game_crud
from src.theThing.games import schemas as game_schemas
from pony.orm import db_session, rollback


@db_session
def test_create_card(test_db):
    # First create a game where to add the card
    game_data = game_schemas.GameCreate(name="Test Game deck", min_players=2, max_players=4)
    created_game = game_crud.create_game(game_data)

    # Create a card
    card_data = CardCreate(
        code="test_code",
        name="Test Card",
        kind=0,
        description="This is a test card",
        number_in_card=1,
        playable=True,
    )

    created_card = card_crud.create_card(card_data, created_game.id)

    assert created_card.model_dump() == {
        "id": 1,
        "code": "test_code",
        "name": "Test Card",
        "kind": 0,
        "description": "This is a test card",
        "number_in_card": 1,
        "state": 2,
        "playable": True,
    }

    game = game_crud.get_game(created_game.id)

    rollback()


def test_create_wrong_card(test_db):
    # First create a game where to add the card
    game_data = game_schemas.GameCreate(name="Test Game deck", min_players=2, max_players=4)
    created_game = game_crud.create_game(game_data)

    # Create a card
    card_data = CardCreate(
        code="test_code",
        name="Test Card",
        kind=7,
        description="This is a test card",
        number_in_card=1,
        playable=True,
    )

    try:
        created_card = card_crud.create_card(card_data, created_game.id)
    except ValueError as e:
        assert e.args[0] == "The kind of the card is not valid"

    rollback()

def