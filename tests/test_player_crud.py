import pytest
from pony.orm import db_session, rollback, ObjectNotFound

from src.theThing.games import crud as game_crud
from src.theThing.games.schemas import GameCreate
from src.theThing.players import crud
from src.theThing.players.models import Player
from src.theThing.players.schemas import PlayerCreate, PlayerUpdate
from .test_setup import test_db


@db_session
def test_create_player(test_db):
    game_data = GameCreate(name="Test Game", min_players=2, max_players=4)
    created_game = game_crud.create_game(game_data)

    player_data = {
        "name": "Test Player",
        "owner": False,
    }

    created_player = crud.create_player(PlayerCreate(**player_data), created_game.id)

    assert created_player.name == player_data["name"]
    assert created_player.owner == player_data["owner"]
    assert game_crud.get_game(created_game.id).model_dump() == {
        "id": 1,
        "name": "Test Game",
        "min_players": 2,
        "max_players": 4,
        "state": 0,
        "play_direction": None,
        "turn_owner": None,
        "players": [
            {
                "id": 1,
                "name": "Test Player",
                "owner": False,
                "table_position": 1,
                "role": None,
                "alive": True,
                "quarantine": False,
            }
        ],
    }
    rollback()


@db_session
def test_create_wrong_player(test_db):
    game_data = GameCreate(name="Test Game", min_players=2, max_players=4)
    created_game = game_crud.create_game(game_data)

    player_data = {
        "name": "Test Player",
        "owner": False,
    }

    created_player = crud.create_player(PlayerCreate(**player_data), created_game.id)

    player2_data = {
        "name": "Test Player",
        "owner": False,
    }
    try:
        created_player2 = crud.create_player(
            PlayerCreate(**player2_data), created_game.id
        )
    except Exception as e:
        assert str(e) == "Player with same name exists"

    assert game_crud.get_game(created_game.id).model_dump() == {
        "id": 1,
        "name": "Test Game",
        "min_players": 2,
        "max_players": 4,
        "state": 0,
        "play_direction": None,
        "turn_owner": None,
        "players": [
            {
                "id": 1,
                "name": "Test Player",
                "owner": False,
                "table_position": 1,
                "role": None,
                "alive": True,
                "quarantine": False,
            }
        ],
    }
    rollback()


@db_session
def test_add_player_to_full_game(test_db):
    game_data = GameCreate(name="Test Game", min_players=1, max_players=2)
    created_game = game_crud.create_game(game_data)
    player1_data = {
        "name": "Test Player 1",
        "owner": True,
    }
    player2_data = {
        "name": "Test Player 2",
        "owner": False,
    }
    player3_data = {
        "name": "Test Player 3",
        "owner": False,
    }
    created_player1 = crud.create_player(PlayerCreate(**player1_data), created_game.id)
    created_player2 = crud.create_player(PlayerCreate(**player2_data), created_game.id)
    try:
        created_player3 = crud.create_player(
            PlayerCreate(**player3_data), created_game.id
        )
    except Exception as e:
        assert str(e) == "Game is full"

    assert game_crud.get_game(created_game.id).model_dump() == {
        "id": 1,
        "name": "Test Game",
        "min_players": 1,
        "max_players": 2,
        "state": 0,
        "play_direction": None,
        "turn_owner": None,
        "players": [
            {
                "id": 1,
                "name": "Test Player 1",
                "owner": True,
                "table_position": 1,
                "role": None,
                "alive": True,
                "quarantine": False,
            },
            {
                "id": 2,
                "name": "Test Player 2",
                "owner": False,
                "table_position": 2,
                "role": None,
                "alive": True,
                "quarantine": False,
            },
        ],
    }


@db_session
def test_get_player(test_db):
    retrieved_player = crud.get_player(1, game_id=1)
    assert retrieved_player.model_dump() == {
        "id": 1,
        "name": "Test Player 1",
        "owner": True,
        "table_position": 1,
        "role": None,
        "alive": True,
        "quarantine": False,
    }


@db_session
def test_get_player_wrong_game(test_db):
    try:
        retrieved_player = crud.get_player(4, game_id=1)
    except ObjectNotFound as e:
        assert str(e) == "Player[4]"


@db_session
def test_update_player(test_db):
    updated_data = {
        "id": 1,
        "table_position": 1,
        "role": 2,
        "alive": False,
        "quarantine": True,
    }
    updated_player = crud.update_player(PlayerUpdate(**updated_data), game_id=1)

    assert updated_player.model_dump() == {
        "id": 1,
        "name": "Test Player 1",
        "owner": True,
        "table_position": 1,
        "role": 2,
        "alive": False,
        "quarantine": True,
    }


@db_session
def test_delete_player(test_db):
    response = crud.delete_player(2, game_id=1)
    assert response == {"message": "Player 2 deleted successfully"}

    try:
        deleted_player = crud.delete_player(2, game_id=1)
    except ObjectNotFound as e:
        assert str(e) == "Player[2]"