import pytest

from .test_setup import test_db
from src.theThing.cards import crud as card_crud
from src.theThing.cards.schemas import CardCreate, CardBase, CardUpdate
from src.theThing.games import crud as game_crud
from src.theThing.games.models import Game
from src.theThing.games import schemas as game_schemas
from src.theThing.players import crud as player_crud
from src.theThing.players import schemas as player_schemas
from pony.orm import db_session, rollback, commit
from src.main import app
from fastapi.testclient import TestClient

# create pytest fixture that runs once for the module before this tests

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_module():
    # create a game
    game_data = game_schemas.GameCreate(
        name="Test Game deck", min_players=4, max_players=5
    )
    created_game = game_crud.create_game(game_data)
    # create the owner player
    player_data = player_schemas.PlayerCreate(name="Player1", owner=True)
    created_player = player_crud.create_player(player_data, created_game.id)

    # create 4 players
    player_data = player_schemas.PlayerCreate(name="Player2", owner=False)
    created_player2 = player_crud.create_player(player_data, created_game.id)
    player_data = player_schemas.PlayerCreate(name="Player3", owner=False)
    created_player3 = player_crud.create_player(player_data, created_game.id)
    player_data = player_schemas.PlayerCreate(name="Player4", owner=False)
    created_player4 = player_crud.create_player(player_data, created_game.id)
    player_data = player_schemas.PlayerCreate(name="Player5", owner=False)
    created_player5 = player_crud.create_player(player_data, created_game.id)

    players_in_game = [
        created_player,
        created_player2,
        created_player3,
        created_player4,
        created_player5,
    ]
    # create 3 cards for each player
    card_data = CardCreate(
        code="def",
        name="Default",
        kind=0,
        description="This is a default card",
        number_in_card=1,
        playable=True,
    )
    for i in range(4):
        created_card = card_crud.create_card(card_data, created_game.id)
        created_card2 = card_crud.create_card(card_data, created_game.id)
        created_card3 = card_crud.create_card(card_data, created_game.id)

        # add the card to the player hand
        card_crud.give_card_to_player(
            created_card.id, players_in_game[i].id, created_game.id
        )
        card_crud.give_card_to_player(
            created_card2.id, players_in_game[i].id, created_game.id
        )
        card_crud.give_card_to_player(
            created_card3.id, players_in_game[i].id, created_game.id
        )

    card_data2 = CardCreate(
        code="lla",
        name="Lanzallamas",
        kind=0,
        description="Lanzallamas",
        number_in_card=1,
        playable=True,
    )
    for i in range(4):
        created_card = card_crud.create_card(card_data2, created_game.id)

        card_crud.give_card_to_player(
            created_card.id, players_in_game[i].id, created_game.id
        )

    # give an extra card to the owner
    extra_card_data = CardCreate(
        code="ext",
        name="Extra",
        kind=0,
        description="Extra",
        number_in_card=1,
        playable=False,
    )

    extra_card = card_crud.create_card(extra_card_data, created_game.id)
    card_crud.give_card_to_player(extra_card.id, created_player.id, created_game.id)

    # start the game
    response = client.post(
        "/game/start", json={"game_id": created_game.id, "player_name": "Player1"}
    )
    assert response.status_code == 200
    # finish setup
    yield


# test case 1: player destination is the player itself
@db_session
def test_play_card_itself(setup_module):
    response = client.put(
        "/game/play",
        json={
            "game_id": 1,
            "player_id": 1,
            "card_id": 1,
            "destination_name": "Player1",
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "The destination player cannot be the same player"
    }

    rollback()  # rollback the changes made in the database


# test case 2: player is not the turn owner
@db_session
def test_play_card_not_turn_owner(setup_module):
    response = client.put(
        "/game/play",
        json={
            "game_id": 1,
            "player_id": 2,
            "card_id": 1,
            "destination_name": "Player1",
        },
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "It is not the player turn"}

    rollback()


# test case 3: card is not in the player hand
@db_session
def test_play_card_not_in_hand(setup_module):
    response = client.put(
        "/game/play",
        json={
            "game_id": 1,
            "player_id": 1,
            "card_id": 5,
            "destination_name": "Player2",
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "The card is not in the player hand or in the deck"
    }

    rollback()


# test case 4: card is not playable
@db_session
def test_play_card_not_playable(setup_module):
    response = client.put(
        "/game/play",
        json={
            "game_id": 1,
            "player_id": 1,
            "card_id": 17,
            "destination_name": "Player2",
        },
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "The card is not playable"}

    rollback()


# test case 5: the destination player is not adjacent to the player
@db_session
def test_play_card_not_adjacent(setup_module):
    response = client.put(
        "/game/play",
        json={
            "game_id": 1,
            "player_id": 1,
            "card_id": 1,
            "destination_name": "Player3",
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "The destination player is not adjacent to the player"
    }

    rollback()


# test case 6: the card is played correctly
@db_session
def test_play_card(setup_module):
    response = client.put(
        "/game/play",
        json={
            "game_id": 1,
            "player_id": 1,
            "card_id": 1,
            "destination_name": "Player2",
        },
    )
    assert response.status_code == 200

    player2_status = player_crud.get_player(2, 1)
    assert player2_status.alive == True  # because the card is not a kill card
    card_played_status = card_crud.get_card(1, 1)
    assert card_played_status.state == 0  # because the card is played


# test case 7: the player cant play because does not have enough cards
@db_session
def test_play_card_not_enough_cards(setup_module):
    response = client.put(
        "/game/play",
        json={
            "game_id": 1,
            "player_id": 2,
            "card_id": 4,
            "destination_name": "Player3",
        },
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Player has less than minimum cards to play"}


# test case 8: the card is played correctly and kills a player
def test_play_card_kill_player(setup_module):
    # add card to player 3 because it has just 4 cards
    new_card_data = CardCreate(
        code="lla",
        name="Lanzallamas",
        kind=0,
        description="Lanzallamas",
        number_in_card=1,
        playable=True,
    )
    new_card_created = card_crud.create_card(new_card_data, 1)
    card_crud.give_card_to_player(new_card_created.id, 2, 1)
    commit()
    response = client.put(
        "/game/play",
        json={
            "game_id": 1,
            "player_id": 2,
            "card_id": 14,
            "destination_name": "Player3",
        },
    )

    player3_status = player_crud.get_player(3, 1)
    player2_status = player_crud.get_player(2, 1)
    card_status = card_crud.get_card(14, 1)
    # get thegame directly from the database to have the updated data
    game_status = game_crud.get_game(1)

    assert response.json() == {"message": "Card played successfully"}
    assert response.status_code == 200
    assert len(player2_status.hand) == 4  # because the card is played
    assert card_status.state == 0  # because the card is played
    assert card_status not in player2_status.hand  # because the card is played
    assert player3_status.alive == False  # because the card is a kill card
    assert (
        game_status.turn_owner == 4
    )  # because the card is a kill card so the next player will be 4
