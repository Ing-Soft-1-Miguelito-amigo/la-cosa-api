import socketio
from src.theThing.cards.schemas import CardBase
from src.theThing.players.schemas import PlayerBase
from src.theThing.games.schemas import GameOut, GameInDB
from urllib.parse import parse_qs
sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
# define an asgi app
socketio_app = socketio.ASGIApp(sio, socketio_path="/")


@sio.event
async def connect(sid, environ):
    print("connect ", sid)
    query_string = environ.get("QUERY_STRING", "")
    params = parse_qs(query_string)
    player_id = params.get("Player-Id", [None])[0]
    game_id = params.get("Game-Id", [None])[0]
    # if the parameters are not present, the connection is rejected
    if not player_id or not game_id:
        return False
    await sio.save_session(sid, {"player_id": player_id, "game_id": game_id})
    sio.enter_room(sid, "g" + game_id)
    sio.enter_room(sid, "p" + player_id)
    print("connect ", sid, "player_id ", player_id, "game_id ", game_id)


@sio.event
async def disconnect(sid):
    print("disconnect ", sid)


async def send_player_status_to_player(player_id: int, player_data: PlayerBase):
    await sio.emit("player_status", player_data.model_dump(), room="p" + str(player_id))


async def send_game_status_to_player(game_id: int, game_data: GameOut):
    """
    Sends the game status to ALL players in the game
    :param game_id:
    :param game_data:
    :return:
    """
    await sio.emit("game_status", game_data.model_dump(), room="g" + str(game_id))


async def send_game_and_player_status_to_players(game_data: GameInDB):
    for player in game_data.players:
        await sio.emit("player_status", player.model_dump(), room="p" + str(player.id))
    game_to_send = GameOut.model_validate_json(game_data.model_dump_json())
    await sio.emit(
        "game_status", game_to_send.model_dump(), room="g" + str(game_data.id)
    )


async def send_discard_event_to_players(game_id: int, player_name: str):
    await sio.emit(
        "discard",
        {"player_name": player_name, "message": player_name + " descartó una carta"},
        room="g" + str(game_id),
    )


async def send_action_event_to_players(
    game_id: int,
    attacking_player: PlayerBase,
    defending_player: PlayerBase,
    action_card: CardBase,
):
    await sio.emit(
        "action",
        data={
            "message": attacking_player.name
            + " le jugo la carta "
            + action_card.name
            + " a "
            + defending_player.name
        },
        room="g" + str(game_id),
    )


async def send_defense_event_to_players(
    game_id: int,
    attacking_player: PlayerBase,
    defending_player: PlayerBase,
    action_card: CardBase,
    defense_card: CardBase,
):
    await sio.emit(
        "defense",
        data={
            "message": defending_player.name
            + " se defendió del ataque de "
            + action_card.name
            + " jugado por "
            + attacking_player.name
            + " con la carta "
            + defense_card.name
        },
        room="g" + str(game_id),
    )


async def send_analysis_to_player(
    player_id: int, hand: [CardBase], attacked_player_name: str
):
    # include all data from the cards except the id
    data_to_send = [card.model_dump(exclude={"id"}) for card in hand]
    await sio.emit(
        "analisis",
        data={
            "message": "Estas son las cartas de" + attacked_player_name,
            "cards": data_to_send,
        },
        room="p" + str(player_id),
    )


async def send_suspicion_to_player(
    player_id: int, card: CardBase, attacked_player_name: str
):
    data_to_send = card.model_dump(exclude={"id"})
    await sio.emit(
        "sospecha",
        data={
            "message": "Esta es una carta de" + attacked_player_name,
            "card": data_to_send,
        },
        room="p" + str(player_id),
    )


async def send_whk_to_player(game_id: int, player: str, hand: [CardBase]):
    data_to_send = [card.model_dump(exclude={"id"}) for card in hand]
    await sio.emit(
        "whisky",
        data={
            "message": player + "jugo whisky y estas son sus cartas!",
            "cards": data_to_send,
        },
        room="g" + str(game_id),
    )
