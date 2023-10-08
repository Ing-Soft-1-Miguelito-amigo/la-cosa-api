from fastapi import APIRouter, WebSocket, HTTPException, WebSocketDisconnect
import asyncio
from typing import Dict, List, Tuple
from src.theThing.players import schemas as player_schemas
from src.theThing.games import schemas as game_schemas
from src.theThing.players import crud as player_crud
from src.theThing.games import crud as game_crud

router = APIRouter()

player_connection_type = Tuple[int, WebSocket]
player_ws_connections: Dict[
    int, player_connection_type
] = {}  # It saves the websocket with the game id


@router.websocket("/ws/game-status/{game_id}/player-status/{player_id}")
async def player_status_ws_endpoint(websocket: WebSocket, game_id: int, player_id: int):
    """
    This endpoint is used to get the status of a player in a game.

    It receives the game_id and the player_id as path parameters. And sends
    the player status via the websocket each time its modified.
    """
    # Check if the player belongs to the game
    try:
        game = game_crud.get_full_game(game_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=e.args[0])
    if not any(player.id == player_id for player in game.players):
        raise HTTPException(status_code=404, detail=f"Player[{player_id}]")

    # Accept the websocket and add it to the connections
    await websocket.accept()
    player_ws_connections[player_id] = (game_id, websocket)
    # send a message to the client to let it know that the connection was successful
    # and tell the key of the player in the dictionary
    await websocket.send_json({"message": "Connection successful", "key": player_id})
    while True:
        try:
            await websocket.receive_text()
        except WebSocketDisconnect:
            break
        finally:
            del player_ws_connections[player_id]


@router.on_event("startup")
async def startup_player_status_event():
    asyncio.create_task(ws_send_player_status())

stop_send_player_status = asyncio.Event()


@router.on_event("shutdown")
async def shutdown_player_status_event():
    # Signal the send_player_status loop to stop on shutdown
    stop_send_player_status.set()

modified_players: List[int] = []


async def ws_send_player_status():
    """
    This function is used to send the player status to the clients
    """
    while not stop_send_player_status.is_set():
        for player_id in modified_players:
            try:
                game_id, websocket = player_ws_connections[player_id]
                player = player_crud.get_player(player_id, game_id)
            except Exception as e:
                raise HTTPException(status_code=404, detail=e.args[0])
            finally:
                modified_players.remove(player_id)
            await websocket.send_json(player.model_dump_json())
        await asyncio.sleep(0.1)


def update_player_status(
    player: player_schemas.PlayerUpdate, player_id: int, game_id: int
):
    """
    This function is used to update the player status in the websocket
    """
    modified_players.append(player_id)
    player_crud.update_player(player, player_id, game_id)


def send_player_new_status(player_id: int):
    """
    This function is used to add a player to the modified players list
    """
    modified_players.append(player_id)
