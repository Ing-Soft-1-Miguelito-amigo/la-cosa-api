from fastapi.testclient import TestClient
from src.main import app
from pony.orm import db_session, rollback, commit
from .test_setup import test_db, clear_db
from src.theThing.games.crud import get_full_game
from src.theThing.cards.schemas import CardCreate, CardUpdate
from src.theThing.cards.crud import create_card, delete_card, update_card

client = TestClient(app)

@db_session
def test_steal_card_success(test_db):
    # Test #1: steal a card from a player with valid data
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

    # Start the game
    game_data = {"game_id": 1, "player_name": "Test Host"}
    response = client.post("/game/start", json=game_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Game 1 started successfully"}
    
    # Steal a card
    steal_data = {"game_id": 1, "player_id": 2}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Card stolen successfully"}


def test_steal_card_empty_deck(test_db):
    # Test #2: steal a card with empty deck
    # Update cards state in the previous game
    card_to_update1 = CardUpdate(id=1, state=0)
    update_card(card_to_update1, 1)
    card_to_update2 = CardUpdate(id=2, state=0)
    update_card(card_to_update2, 1)

    # Steal a card. It should not generate any problems
    steal_data = {"game_id": 1, "player_id": 1}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Card stolen successfully"}
    rollback()


def test_steal_card_with_invalid_player_id(test_db):
    # Test #2: steal a card with invalid player id
    steal_data = {"game_id": 1, "player_id": 5}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 422
    assert response.json() == {"detail": "Player not found"}
    rollback()


def test_steal_with_no_cards_indeck(test_db):
    # Test #2: steal a card from a player with no cards in deck
    # Delete the 35 cards on the previous test game to empty the deck
    for i in range(1, 36):
        response = delete_card(i, 1)
        assert response == {"message": f"Card {i} deleted successfully from game 1"}
    commit()
    
    # Steal a card
    steal_data = {"game_id": 1, "player_id": 2}
    response = client.put("/game/steal", json=steal_data)
    print(response.json())
    assert response.status_code == 422
    assert response.json() == {"detail": "Non existent cards in the deck"}


def test_steal_card_on_not_started_game(test_db):
    # Create a game first
    game_data = {
        "game": {"name": "Test Game 2", "min_players": 4, "max_players": 4},
        "host": {"name": "Test Host"},
    }
    client.post("/game/create", json=game_data)

    # Players data for joining
    join_data = {
        "players": [
            {"game_id": 2, "player_name": "Test Player 6"},
            {"game_id": 2, "player_name": "Test Player 7"},
            {"game_id": 2, "player_name": "Test Player 8"},
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

    # Steal a card
    steal_data = {"game_id": 2, "player_id": 6}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 422
    assert response.json() == {"detail": "Game has not started yet"}
    rollback()
    

def test_steal_card_with_empty_data():
    # Test #2: steal a card with empty data
    steal_data = {}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 422
    assert response.json() == {"detail": "Input data cannot be empty"}


def test_steal_card_with_invalid_game_id(test_db):
    # Test #2: steal a card with invalid game id
    steal_data = {"game_id": 3, "player_id": 2}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}
