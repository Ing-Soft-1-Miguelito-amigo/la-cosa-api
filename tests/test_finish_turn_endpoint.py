import pytest
from fastapi.testclient import TestClient
from src.main import app
from pony.orm import db_session, rollback
from tests.test_setup import test_db, clear_db


client = TestClient(app)


@db_session
def test_finish_turn_not_started(test_db):
    # Test case 1: Game exists, but it is not started
    game_data = {
        "game": {"name": "Prueba", "min_players": 4, "max_players": 6},
        "host": {"name": "Test Host"},
    }
    response = client.post("/game/create", json=game_data)

    game_id = response.json().get("game_id")
    player_name = "Test Host"
    game_data = {"game_id": game_id, "player_name": player_name}

    # finish the turn
    response = client.put(
        "/turn/finish", json={"game_id": game_id, "player_id": 1}
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "La partida aún no ha comenzado"}

    rollback()


@db_session
def test_finish_turn_not_started(test_db):
    # Test case 2: Game exists, data is valid, and the game starts successfully
    game_data = {
        "game": {"name": "Prueba", "min_players": 4, "max_players": 6},
        "host": {"name": "Test Host"},
    }
    response = client.post("/game/create", json=game_data)

    game_id = response.json().get("game_id")
    player_name = "Test Host"
    game_data = {"game_id": game_id, "player_name": player_name}

    # join a few players
    client.post(
        "/game/join", json={"game_id": game_id, "player_name": "Not Host"}
    )
    client.post(
        "/game/join", json={"game_id": game_id, "player_name": "Not Host2"}
    )
    client.post(
        "/game/join", json={"game_id": game_id, "player_name": "Not Host3"}
    )

    # start the game
    response = client.post(
        "/game/start", json={"game_id": game_id, "player_name": player_name}
    )

    # finish the turn
    response = client.put(
        "/turn/finish", json={"game_id": game_id, "player_id": 1}
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "El turno aún no ha terminado"}

    rollback()


@db_session
def test_finish_turn_next_player(test_db):
    # Test case 3: Game exists, data is valid, and the game starts successfully
    # steal a card
    response = client.put("/game/steal", json={"game_id": 1, "player_id": 1})

    # discard a card
    response = client.put(
        "/game/discard", json={"game_id": 1, "player_id": 1, "card_id": 1}
    )

    # finish the turn
    response = client.put("/turn/finish", json={"game_id": 1, "player_id": 1})

    assert response.json() == {"message": "Turno finalizado con éxito"}
