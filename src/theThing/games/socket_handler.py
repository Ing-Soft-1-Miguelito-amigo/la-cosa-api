import socketio
from src.theThing.cards.schemas import CardBase
from src.theThing.players.schemas import PlayerBase
from src.theThing.games.schemas import GameOut, GameInDB

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
# define an asgi app
socketio_app = socketio.ASGIApp(sio)


@sio.event
async def connect(sid, environ):
    print("connect ", sid)
    player_id = environ.get("HTTP_PLAYER_ID")
    game_id = environ.get("HTTP_GAME_ID")
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
    await sio.emit(
        "player_status", player_data.model_dump(), room="p" + str(player_id)
    )


async def send_game_status_to_player(game_id: int, game_data: GameOut):
    await sio.emit(
        "game_status", game_data.model_dump(), room="g" + str(game_id)
    )


async def send_game_and_player_status_to_players(game_data: GameInDB):
    for player in game_data.players:
        await sio.emit(
            "player_status", player.model_dump(), room="p" + str(player.id)
        )
    game_to_send = GameOut.model_validate_json(game_data.model_dump_json())
    await sio.emit(
        "game_status", game_to_send.model_dump(), room="g" + str(game_data.id)
    )


async def send_discard_event_to_players(game_id: int, player_name: str):
    await sio.emit(
        "discard", {"player_name": player_name,
                    "message": player_name + " descartó una carta"}, room="g" + str(game_id)
    )


async def send_action_event_to_players(game_id: int, attacking_player: PlayerBase, defending_player: PlayerBase, action_card: CardBase):
    await sio.emit(
        "action", 
        data={
        "message": attacking_player.name + " le aplicó la carta "
        + action_card.name + " a " + defending_player.name
        }, 
        room="g" + str(game_id)
    )


async def send_defense_event_to_players(game_id: int, attacking_player: PlayerBase, defending_player: PlayerBase, action_card: CardBase, defense_card: CardBase):
    await sio.emit(
        "defense", 
        data={
        "message": defending_player.name + " se defendió del ataque de " 
        + action_card.name + " jugado por " + attacking_player.name + " con la carta " + defense_card.name}, 
        room="g" + str(game_id)
    )