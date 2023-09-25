from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from pony.orm import db_session, ObjectNotFound

from src.games import crud, schemas
from src.models.db import db
from . import populate_database

app = FastAPI()  # Create an FastAPI instance app for testing purposes


@app.get("/games")
async def get_games_base_form():
    return crud.get_all_games()


@app.get("/gamesINDB",
         status_code=status.HTTP_200_OK)
async def get_games_indb_form():
    return crud.get_all_games_in_db()


@app.get("/games/{game_id}",
         status_code=status.HTTP_200_OK)
async def get_game(game_id: int):
    return crud.get_game(game_id)


@app.post("/games/create/",
          status_code=status.HTTP_201_CREATED)
async def create_game(new_game: schemas.GameCreate):
    return crud.create_game(new_game)


@app.delete("/games/{game_id}",
            status_code=status.HTTP_200_OK)
async def delete_game(game_id: int):
    return crud.delete_game(game_id)


@app.put("/games/{game_id}",
         status_code=status.HTTP_200_OK)
async def update_game(game_id: int, game: schemas.GameUpdate):
    # update a game
    return crud.update_game(game_id, game)


client = TestClient(app)  # Create a TestClient instance client for testing purposes
db.bind(provider='sqlite', filename='test_database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)
# load data for test
populate_database.load_data_for_test()


@db_session
def test_read_games_base_form():
    response = client.get("/games")
    assert response.status_code == 200
    assert response.json() == [{"name": "Uno", "min_players": 4, "max_players": 12},
                               {"name": "Dos", "min_players": 2, "max_players": 10},
                               {"name": "Tres", "min_players": 3, "max_players": 8}, ]


@db_session
def test_read_games_INDB_form():
    response = client.get("/gamesINDB")
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "name": "Uno", "min_players": 4, "max_players": 12,
                                "password": "", "state": 0, "players": [], "play_direction": None, "turn_owner": None},
                               {"id": 2, "name": "Dos", "min_players": 2, "max_players": 10,
                                "password": "", "state": 0, "players": [], "play_direction": None, "turn_owner": None},
                               {"id": 3, "name": "Tres", "min_players": 3, "max_players": 8,
                                "password": "securepassword", "state": 0, "players": [], "play_direction": None,
                                "turn_owner": None}]


@db_session
def test_get_single_game():
    response = client.get("/games/3")
    assert response.status_code == 200
    assert response.json() == {"id": 3, "name": "Tres", "min_players": 3, "max_players": 8,
                               "state": 0, "players": [], "play_direction": None, "turn_owner": None}


@db_session
def test_create_delete_game():
    response = client.post("/games/create/",
                           json={"name": "Cuatro", "min_players": 2, "max_players": 4, "password": "testpassword"},
                           )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Cuatro"
    assert "id" in data
    game_id = data["id"]

    response = client.get(f"/games/{game_id}")
    assert response.status_code == 200
    data = response.json()
    assert data == {"id": game_id, "name": "Cuatro", "min_players": 2, "max_players": 4,
                    "state": 0, "players": [], "play_direction": None, "turn_owner": None}

    response = client.delete(f"/games/{game_id}")
    assert response.status_code == 200
    try:
        response = client.get(f"/games/{game_id}")
    except ObjectNotFound:
        assert True
    assert response.json() == {"message": f"Game {game_id} deleted successfully"}


@db_session
def test_update_game():
    response = client.put("/games/3",
                          json={"state": 1, "play_direction": True, "turn_owner": 1},
                          )
    assert response.status_code == 200
    data = response.json()
    assert data["state"] == 1
    assert data["play_direction"] == True
    assert data["turn_owner"] == 1

    response = client.get("/games/3")
    assert response.status_code == 200
    data = response.json()
    assert data["state"] == 1
    assert data["play_direction"] == True
    assert data["turn_owner"] == 1
@db_session
def test_create_wrong_game():
    try:
        response = client.post("/games/create/",
                           json={"min_players": 2, "max_players": 4})
    except ValueError:
        assert True
