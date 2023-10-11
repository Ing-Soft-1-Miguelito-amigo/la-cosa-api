from fastapi.testclient import TestClient
from src.main import app
from pony.orm import db_session, rollback, commit
from .test_setup import test_db, clear_db
from src.theThing.games.crud import get_full_game, update_game
from src.theThing.games.schemas import GameUpdate
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
            "game_id": 1,
        }
        playerid += 1

    # Start the game
    game_data = {"game_id": 1, "player_name": "Test Host"}
    response = client.post("/game/start", json=game_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Game 1 started successfully"}

    # Steal a card
    steal_data = {"game_id": 1, "player_id": 1}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Card stolen successfully"}


def test_steal_card_empty_deck(test_db):
    # Test #2: steal a card with empty deck

    # Update cards state to played in the previous game
    game = get_full_game(1)
    for card in game.deck:
        card_to_update = CardUpdate(id=card.id, state=0)
        update_card(card_to_update, 1)
    commit()

    gameupdate = GameUpdate(state=1, play_direction=True, turn_owner=2)
    update_game(1, gameupdate)
    commit()
    # Steal a card. It should not generate any problems
    steal_data = {"game_id": 1, "player_id": 2}
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
    # Delete the 31 cards on the previous test game to empty the deck
    game = get_full_game(1)
    for card in game.deck:
        response = delete_card(card.id, 1)
        assert response == {
            "message": f"Card {card.id} deleted successfully from game 1"
        }
    commit()

    gameupdate = GameUpdate(state=1, play_direction=True, turn_owner=3)
    update_game(1, gameupdate)
    commit()
    # Steal a card
    steal_data = {"game_id": 1, "player_id": 3}
    response = client.put("/game/steal", json=steal_data)
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
            "game_id": 2,
        }
        playerid += 1

    # Steal a card
    steal_data = {"game_id": 2, "player_id": 5}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 422
    assert response.json() == {"detail": "Game has not started yet"}


def test_steal_card_2_times(test_db):
    # Test: try to steal a card 2 times
    # start the previous game
    game_data = {"game_id": 2, "player_name": "Test Host"}
    response = client.post("/game/start", json=game_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Game 2 started successfully"}

    # Steal a card
    steal_data = {"game_id": 2, "player_id": 5}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Card stolen successfully"}

    # Steal a card again
    steal_data = {"game_id": 2, "player_id": 5}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 422
    assert response.json() == {"detail": "Player hand is full"}
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
