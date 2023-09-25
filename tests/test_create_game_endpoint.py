from fastapi.testclient import TestClient
from src.main import app
from src.models.db import db


client = TestClient(app)
db.bind(provider='sqlite', filename='test_create_game.sqlite', create_db=True)
db.generate_mapping(create_tables=True)


def test_create_game_success():
    # Test creating a game with valid data
    game_data = {"name": "Test Game", "min_players": 4, "max_players": 6}
    response = client.post("/game/create", json=game_data)
    assert response.status_code == 201
    assert response.json() == {"message": "Game 'Test Game' created successfully"}


def test_create_game_empty_name():
    # Test creating a game with an empty name
    game_data = {"name": "", "min_players": 4, "max_players": 6}
    response = client.post("/game/create", json=game_data)
    assert response.status_code == 422
    assert "Game name cannot be empty" in response.text


def test_create_game_invalid_min_players():
    # Test creating a game with invalid minimum players
    game_data = {
        "name": "Test Game",
        "min_players": 2,  # Less than the required minimum of 4
        "max_players": 6,
    }
    response = client.post("/game/create", json=game_data)
    assert response.status_code == 422
    assert "Minimum players cannot be less than 4" in response.text


def test_create_game_invalid_max_players():
    # Test creating a game with invalid maximum players
    game_data = {
        "name": "Test Game",
        "min_players": 4,
        "max_players": 15,  # Greater than the allowed maximum of 12
    }
    response = client.post("/game/create", json=game_data)
    assert response.status_code == 422
    assert "Maximum players cannot be greater than 12" in response.text
