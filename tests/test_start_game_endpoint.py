from fastapi.testclient import TestClient
from src.main import app
from pony.orm import db_session, rollback
from tests.test_setup import test_db

client = TestClient(app)


@db_session
def test_start_game_successful(test_db):
    # Test case 1: Game exists, data is valid, and the game starts successfully
    game_data = {
        "game": {"name": "Prueba", "min_players": 4, "max_players": 6},
        "host": {"name": "Test Host"},
    }
    response = client.post("/game/create", json=game_data)

    game_id = response.json().get("game_id")
    player_name = "Test Host"
    game_data = {"game_id": game_id, "player_name": player_name}

    response = client.post("/game/start", json=game_data)
    assert response.status_code == 200
    assert response.json() == {"message": f"Game {game_id} started successfully"}


@db_session
def test_start_nonexistent_game(test_db):
    # Test case 2: Game does not exist
    game_id = 100
    player_name = "Test Host"
    game_data = {"game_id": game_id, "player_name": player_name}

    response = client.post("/game/start", json=game_data)
    assert response.status_code == 404
    assert response.json() == {"detail": f"Game[100]"}
    rollback()


@db_session
def test_start_game_with_invalid_host(test_db):
    # Test case 3: Game exists, but the host is not a player
    game_data = {
        "game": {"name": "Prueba2", "min_players": 4, "max_players": 6},
        "host": {"name": "Test Host"},
    }
    response = client.post("/game/create", json=game_data)

    game_id = response.json().get("game_id")
    player_name = "Not Host"
    game_data = {"game_id": game_id, "player_name": player_name}

    response = client.post("/game/start", json=game_data)
    assert response.status_code == 422
    assert response.json() == {"detail": "The host is not in the game"}
