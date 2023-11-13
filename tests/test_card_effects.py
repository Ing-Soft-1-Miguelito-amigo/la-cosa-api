import pytest
from src.theThing.games import crud as games_crud
from src.theThing.games import schemas as games_schemas
from src.theThing.players import crud as players_crud
from src.theThing.players import schemas as players_schemas
from src.theThing.cards.effect_applications import effect_applications as cards_effect_applications
from src.theThing.cards import crud as cards_crud
from src.theThing.cards import schemas as cards_schemas
from src.theThing.turn import crud as turn_crud
from src.theThing.turn import schemas as turn_schemas
from src.main import app
from fastapi.testclient import TestClient
from tests.test_setup import test_db, clear_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    # create a game, add 4 players and create a turn
    game_data = games_schemas.GameCreate(
        name="Test Game deck", min_players=4, max_players=5
    )
    created_game = games_crud.create_game(game_data)
    # create the owner player
    player_data = players_schemas.PlayerCreate(name="Player1", owner=True)
    created_player = players_crud.create_player(player_data, created_game.id)

    # create 3 players
    player_data = players_schemas.PlayerCreate(name="Player2", owner=False)
    created_player2 = players_crud.create_player(player_data, created_game.id)
    player_data = players_schemas.PlayerCreate(name="Player3", owner=False)
    created_player3 = players_crud.create_player(player_data, created_game.id)
    player_data = players_schemas.PlayerCreate(name="Player4", owner=False)
    created_player4 = players_crud.create_player(player_data, created_game.id)
    created_player4 = players_crud.update_player(players_schemas.PlayerUpdate(role=3),
                                                 created_player4.id, created_game.id)
    # create a turn, owner is player 1, exchange destination is player 2
    turn_crud.create_turn(created_game.id, 1, created_player2.name)

    # set turn to state 1 (deciding)
    turn_data = turn_schemas.TurnCreate(state=1)
    turn_crud.update_turn(created_game.id, turn_data)


@pytest.mark.asyncio
async def test_lla(test_db):
    # this card kills the destination player
    card = cards_schemas.CardCreate(code='lla',
                                    name='Lanzallamas',
                                    kind=0,
                                    description='Lanzallamas',
                                    number_in_card=1,
                                    playable=True)
    card = cards_crud.create_card(card, 1)
    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)
    destination_player = players_crud.get_player(2, 1)
    game = await cards_effect_applications[card.code](full_game, player, destination_player, card)

    updated_card = cards_crud.get_card(card.id, 1)
    updated_d_player = players_crud.get_player(2, 1)

    assert updated_card.state == 0
    assert updated_d_player.alive == False
    assert game.turn.destination_player_exchange == "Player3"


@pytest.mark.asyncio
async def test_vte(test_db):
    card = cards_schemas.CardCreate(code='vte',
                                    name='Vigila tus espaldas',
                                    kind=0,
                                    description='Vigila tus espaldas',
                                    number_in_card=1,
                                    playable=True)
    card = cards_crud.create_card(card, 1)
    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)

    game = await cards_effect_applications[card.code](full_game, player, player, card)

    updated_card = cards_crud.get_card(card.id, 1)
    assert updated_card.state == 0
    assert game.turn.destination_player_exchange == "Player4"
    assert game.play_direction != full_game.play_direction


@pytest.mark.asyncio
async def test_cdl(clear_db):
    card = cards_schemas.CardCreate(code='cdl',
                                    name='Cambio de lugar',
                                    kind=0,
                                    description='Cambio de lugar',
                                    number_in_card=1,
                                    playable=True)
    card = cards_crud.create_card(card, 1)
    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)
    player_tb = player.table_position
    destination_player = players_crud.get_player(3, 1)
    destination_player_tb = destination_player.table_position
    game = await cards_effect_applications[card.code](full_game, player, destination_player, card)

    updated_card = cards_crud.get_card(card.id, 1)
    updated_player = players_crud.get_player(1, 1)
    updated_d_player = players_crud.get_player(3, 1)

    assert updated_card.state == 0
    assert updated_player.table_position == destination_player_tb
    assert updated_d_player.table_position == player_tb
    assert game.turn.destination_player_exchange == "Player3"


@pytest.mark.asyncio
async def test_mvc(clear_db):
    # this card does the same as cdl
    card = cards_schemas.CardCreate(code='mvc',
                                    name='Mas vale que corras',
                                    kind=0,
                                    description='Mas vale que corras',
                                    number_in_card=1,
                                    playable=True)
    card = cards_crud.create_card(card, 1)
    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)
    player_tb = player.table_position
    destination_player = players_crud.get_player(4, 1)
    destination_player_tb = destination_player.table_position

    game = await cards_effect_applications[card.code](full_game, player, destination_player, card)

    updated_card = cards_crud.get_card(card.id, 1)
    updated_player = players_crud.get_player(1, 1)
    updated_d_player = players_crud.get_player(4, 1)

    assert updated_card.state == 0
    assert updated_player.table_position == destination_player_tb
    assert updated_d_player.table_position == player_tb
    assert game.turn.destination_player_exchange == "Player4"


@pytest.mark.asyncio
async def test_cua(test_db):
    card = cards_schemas.CardCreate(code='cua',
                                    name='Cuarentena',
                                    kind=0,
                                    description='Cuarentena',
                                    number_in_card=1,
                                    playable=True)
    card = cards_crud.create_card(card, 1)
    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)
    destination_player = players_crud.get_player(3, 1)

    game = await cards_effect_applications[card.code](full_game, player, destination_player, card)

    updated_card = cards_crud.get_card(card.id, 1)
    updated_d_player = players_crud.get_player(3, 1)

    assert updated_card.state == 0
    assert updated_d_player.quarantine == 2



