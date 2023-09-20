from fastapi import FastAPI, status, HTTPException
from fastapi.testclient import TestClient
from ..entities import Game # imports database definition
from ..schemas import GameBase, GameCreate, GameOut, GameInDB # imports schemas
from pony.orm import db_session


app = FastAPI()  # Create an FastAPI instance app for testing purposes

@app.get("/")
async def root():
    return {"message": "Hello World this is a test API"}


@app.get("/games")
async def get_games_base_form():
    with db_session:
        games = Game.select()
        result = [GameBase.model_validate(game) for game in games]
    return result

@app.get("/gamesINDB",
         status_code=status.HTTP_200_OK)
async def get_games_indb_form():
    with db_session:
        games = Game.select()
        result = [GameInDB.model_validate(game) for game in games]
    return result


@app.get("/games/{game_id}",
         status_code=status.HTTP_200_OK)
async def get_game(game_id: int):
    with db_session:
        try:
            game = Game[game_id]
            response = GameInDB.model_validate(game)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Game {game_id} not found")
    return response


@app.post("/games/create/",
          response_model=GameOut,
          status_code=status.HTTP_201_CREATED)
async def create_game(new_game: GameCreate):
    with db_session:
        if new_game.password:
            game = Game(name=new_game.name,
                        min_players=new_game.min_players,
                        max_players=new_game.max_players,
                        password=new_game.password)
        else:
            game = Game(name=new_game.name,
                        min_players=new_game.min_players,
                        max_players=new_game.max_players)
        game.flush()
        response = GameOut.model_validate(game)
    return response

@app.delete("/games/{game_id}",
            status_code=status.HTTP_200_OK)
async def delete_game(game_id: int):
    with db_session:
        game = Game[game_id]
        game.delete()
    return {"message": f"Game {game_id} deleted successfully"}


client = TestClient(app)  # Create a TestClient instance client for testing purposes


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World this is a test API"}

def test_read_games_base_form():
    response = client.get("/games")
    assert response.status_code == 200
    assert  response.json() == [{"name": "Uno", "min_players": 4, "max_players": 12}, 
                                {"name": "Dos", "min_players": 2, "max_players": 10}, 
                                {"name": "Tres", "min_players": 3, "max_players": 8},]
    print(response.json())

def test_read_games_INDB_form():
    response = client.get("/gamesINDB")
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "name": "Uno", "min_players": 4, "max_players": 12, 
                                "password": "", "state": 0, "play_direction": None, "turn_owner": None}, 
                                {"id": 2, "name": "Dos", "min_players": 2, "max_players": 10, 
                                 "password":"", "state": 0, "play_direction": None, "turn_owner": None}, 
                                {"id": 3, "name": "Tres", "min_players": 3, "max_players": 8, 
                                 "password": "securepassword","state": 0, "play_direction": None, "turn_owner": None}]


def test_get_single_game():
    response = client.get("/games/3")
    assert response.status_code == 200
    assert response.json() == {"id": 3, "name": "Tres", "min_players": 3, "max_players": 8,
                               "password": "securepassword", "state": 0, "play_direction": None, 
                               "turn_owner": None}


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
                    "password": "testpassword", "state": 0, "play_direction": None, 
                    "turn_owner": None}

    response = client.delete(f"/games/{game_id}")
    assert response.status_code == 200

    response = client.get(f"/games/{game_id}")
    assert response.status_code == 404