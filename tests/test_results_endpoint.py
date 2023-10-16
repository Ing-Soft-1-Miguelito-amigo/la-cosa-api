from fastapi.testclient import TestClient
from src.main import app
from pony.orm import db_session, rollback
from tests.test_setup import test_db, clear_db
from src.theThing.players.crud import update_player
from src.theThing.players.schemas import PlayerUpdate

client = TestClient(app)


@db_session
def test_get_result_of_inplay_game(test_db):
    """
    Test case 1: Game exists, but it is not yet finished
    """
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

    response = client.post("/game/start", json=game_data)

    response = client.get(f"/game/{game_id}/results")
    assert response.status_code == 422
    assert response.json() == {"detail": "La partida aún no ha finalizado"}
    rollback()


@db_session
def test_get_result_of_nonexistent_game():
    """
    Test case 2: Game does not exist
    """
    game_id = 100
    response = client.get(f"/game/{game_id}/results")
    assert response.status_code == 404
    assert response.json() == {"detail": f"Game[{game_id}]"}
    rollback()


@db_session
def test_get_result_of_finished_game(test_db):
    """
    Test case 3: Game is finished
    """
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

    client.post("/game/start", json=game_data)

    update_player(
        PlayerUpdate(alive=False), 2, game_id
    )
    update_player(
        PlayerUpdate(alive=False), 3, game_id
    )
    update_player(
        PlayerUpdate(alive=False), 4, game_id
    )

    response = client.get(f"/game/{game_id}/results")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Partida finalizada con éxito",
        "game_id": game_id,
        "winners": [1]
    }
    rollback()
