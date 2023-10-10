import socketio
from src.theThing.players.schemas import PlayerBase

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode='asgi')
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
    await sio.emit("player_status", player_data.model_dump(), room="p" + str(player_id))

