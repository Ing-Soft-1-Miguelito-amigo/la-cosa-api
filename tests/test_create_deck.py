from fastapi.testclient import TestClient
from src.main import app
from src.theThing.games.crud import get_full_game
from pony.orm import db_session, rollback
from tests.test_setup import test_db, clear_db

client = TestClient(app)


@db_session
def test_create_deck_4_players_success(test_db):
    # Test #1: create a deck with valid data
    # Create a game first
    game_data = {
        "game": {"name": "Test Game", "min_players": 4, "max_players": 5},
        "host": {"name": "Test Host"},
    }
    response = client.post("/game/create", json=game_data)

    # Players data for joining
    join_data = {
        "players": [
            {"game_id": 1, "player_name": "Test Player 2"},
            {"game_id": 1, "player_name": "Test Player 3"},
            {"game_id": 1, "player_name": "Test Player 4"},
        ]
    }

    # Join players to the game
    playerid = 2
    for player in join_data["players"]:
        response = client.post("/game/join", json=player)
        assert response.status_code == 200
        assert response.json() == {
            "message": "Player joined game successfully",
            "player_id": playerid,
        }
        playerid += 1

    # Start the game. Create the deck
    game_data = {"game_id": 1, "player_name": "Test Host"}
    response = client.post("/game/start", json=game_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Game 1 started successfully"}

    # Check deck size
    game = get_full_game(1)
    assert len(game.deck) == 35
    # Check that the deck contains the card "tth"
    assert any(card.code == "tth" for card in game.deck)


@db_session
def test_create_deck_6_players_success(test_db):
    # Test #1: create a deck with valid data
    # Create a game first
    game_data = {
        "game": {"name": "Test Game 2", "min_players": 4, "max_players": 6},
        "host": {"name": "Test Host 2"},
    }
    response = client.post("/game/create", json=game_data)

    # Players data for joining
    join_data = {
        "players": [
            {"game_id": 2, "player_name": "Test Player 6"},
            {"game_id": 2, "player_name": "Test Player 7"},
            {"game_id": 2, "player_name": "Test Player 8"},
            {"game_id": 2, "player_name": "Test Player 9"},
            {"game_id": 2, "player_name": "Test Player 10"},
        ]
    }

    # Join players to the game
    playerid = 6
    for player in join_data["players"]:
        response = client.post("/game/join", json=player)
        assert response.status_code == 200
        assert response.json() == {
            "message": "Player joined game successfully",
            "player_id": playerid,
        }
        playerid += 1

    # Start the game. Create the deck
    game_data = {"game_id": 2, "player_name": "Test Host 2"}
    response = client.post("/game/start", json=game_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Game 2 started successfully"}

    # Check deck size
    game = get_full_game(2)
    assert len(game.deck) == 36
    # Check that the deck contains the card "tth"
    assert any(card.code == "tth" for card in game.deck)
