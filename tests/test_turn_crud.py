import pytest
from pony.orm import db_session, rollback, ObjectNotFound

from src.theThing.games import crud as game_crud
from src.theThing.games.schemas import GameCreate, GameOut
from src.theThing.turn import crud
from src.theThing.turn.schemas import TurnCreate, TurnOut
from .test_setup import test_db, clear_db


@db_session
def test_create_turn(test_db):
    game_data = GameCreate(name="Test Game", min_players=4, max_players=6)
    created_game = game_crud.create_game(game_data)

    turn_data = {
        "game": created_game.id,
        "owner": 1,
    }

    created_turn = crud.create_turn(turn_data["game"], turn_data["owner"])

    assert created_turn.owner == turn_data["owner"]
    assert game_crud.get_game(created_game.id).model_dump() == {
        "id": 1,
        "name": "Test Game",
        "min_players": 4,
        "max_players": 6,
        "state": 0,
        "play_direction": None,
        "turn_owner": None,
        "turn": {
            "destination_player": "",
            "owner": 1,
            "played_card": None,
            "response_card": None,
            "state": 0,
        },
        "players": [],
    }


@db_session
def test_update_turn(test_db):
    updated_turn = crud.update_turn(
        1,
        TurnCreate(
            owner=1,
            played_card=1,
            destination_player="TestPlayer1",
            response_card=3,
            state=1,
        ),
    )

    assert updated_turn.owner == 1
    assert updated_turn.played_card == 1
    assert updated_turn.destination_player == "TestPlayer1"
    assert updated_turn.response_card == 3
    assert updated_turn.state == 1
    assert game_crud.get_game(1).model_dump() == {
        "id": 1,
        "name": "Test Game",
        "min_players": 4,
        "max_players": 6,
        "state": 0,
        "play_direction": None,
        "turn_owner": None,
        "turn": {
            "destination_player": "TestPlayer1",
            "owner": 1,
            "played_card": 1,
            "response_card": 3,
            "state": 1,
        },
        "players": [],
    }

    rollback()
