import pytest
from pony.orm import db_session, commit, rollback
from src.theThing.games import crud
from src.theThing.games.models import Game
from src.theThing.games.schemas import (
    GameCreate,
    GameUpdate,
    GameOut,
    GameBase,
    GameInDB,
)
from .test_setup import test_db, clear_db


@db_session
def test_create_game(test_db):
    game_data = {
        "name": "Test Game",
        "min_players": 2,
        "max_players": 4,
        "password": "test_password",
    }

    created_game = crud.create_game(GameCreate(**game_data))

    assert created_game.name == game_data["name"]
    assert created_game.min_players == game_data["min_players"]
    assert created_game.max_players == game_data["max_players"]

    rollback()


@db_session
def test_create_wrong_game(test_db):
    game_data = {
        "name": "Test Game",
        "min_players": 2,
        "max_players": 4,
        "password": "test_password",
    }

    try:
        created_game = crud.create_game(GameCreate(**game_data))
    except Exception as e:
        assert e.args[0] == "Game already exists"

    rollback()


@db_session
def test_get_game(test_db):
    game = Game(name="Test Game", min_players=2, max_players=4)
    game.flush()

    retrieved_game = crud.get_game(game.id)

    assert retrieved_game.id == game.id
    assert retrieved_game.name == game.name

    rollback()


@db_session
def test_get_all_games(test_db):
    game1 = Game(name="Game 1", min_players=2, max_players=4)
    game2 = Game(name="Game 2", min_players=3, max_players=6)
    game1.flush()
    game2.flush()

    games = crud.get_all_games()

    assert len(games) == 2
    assert games == [GameBase(**game1.to_dict()), GameBase(**game2.to_dict())]

    rollback()


@db_session
def test_delete_game(test_db):
    game = Game(name="Test Game", min_players=2, max_players=4)
    game.flush()

    crud.delete_game(game.id)

    deleted_game = Game.get(id=game.id)

    assert deleted_game is None

    rollback()


@db_session
def test_get_all_games_in_db(test_db):
    game1 = Game(name="Game 6", min_players=2, max_players=4)
    game2 = Game(name="Game 8", min_players=3, max_players=6)
    game1.flush()
    game2.flush()

    games = crud.get_all_games_in_db()

    assert len(games) == 2
    assert [game.model_dump() for game in games] == [
        {
            "id": game1.id,
            "name": game1.name,
            "min_players": game1.min_players,
            "max_players": game1.max_players,
            "password": game1.password,
            "state": game1.state,
            "play_direction": game1.play_direction,
            "turn_owner": game1.turn_owner,
            "players": [],
            "deck": [],
        },
        {
            "id": game2.id,
            "name": game2.name,
            "min_players": game2.min_players,
            "max_players": game2.max_players,
            "password": game2.password,
            "state": game2.state,
            "play_direction": game2.play_direction,
            "turn_owner": game2.turn_owner,
            "players": [],
            "deck": [],
        },
    ]

    rollback()


@db_session
def test_update_game(test_db):
    game = Game(name="Test Game", min_players=2, max_players=4)
    game.flush()

    updated_data = {
        "state": 1,
        "play_direction": True,
        "turn_owner": 5,
    }

    updated_game = crud.update_game(game.id, GameUpdate(**updated_data))

    assert updated_game.state == updated_data["state"]
    assert updated_game.play_direction == updated_data["play_direction"]
    assert updated_game.turn_owner == updated_data["turn_owner"]

    rollback()
