from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .schemas import GameCreate, GameUpdate
from ..players.schemas import PlayerCreate
from ..players.crud import create_player
from .crud import create_game, get_game, update_game, get_full_game
from .utils import verify_data_create, verify_data_start, verify_finished_game
from pony.orm import ObjectNotFound as ExceptionObjectNotFound

# Create an APIRouter instance for grouping related endpoints
router = APIRouter()


class GameWithHost(BaseModel):
    """
    Pydantic model to validate the data received from the client
    """

    game: GameCreate
    host: PlayerCreate


# Endpoint to create a game
@router.post("/game/create", status_code=201)
async def create_new_game(game_data: GameWithHost):
    """
    Create a new game with a host player.

    Args:
        game_data (GameWithHost): Pydantic model containing game and host player information.

    Returns:
        dict: A JSON response indicating the success of the game creation.

    Raises:
        HTTPException: If there is an error during game creation or data validation.
    """
    game_name = game_data.game.name
    min_players = game_data.game.min_players
    max_players = game_data.game.max_players
    host_name = game_data.host.name

    # Check that name and host are not empty
    verify_data_create(game_name, min_players, max_players, host_name)

    game = GameCreate(name=game_name, min_players=min_players, max_players=max_players)
    host = PlayerCreate(name=host_name, owner=True)

    # Perform logic to save the game in the database
    try:
        created_game = create_game(game)
        # assign the host to the game
        create_player(host, created_game.id)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {
        "message": f"Game '{game_name}' created by '{host_name}' successfully",
        "game_id": created_game.id,
    }


@router.post("/game/start")
async def start_game(game_start_info: dict):
    """
    Start a game with the provided game start information.

    Parameters:
        game_start_info (dict): A dictionary containing game start information.
            It should include the following keys:
            - 'game_id' (str): The unique identifier of the game.
            - 'player_name' (str): The name of the host player.

    Returns:
        dict: A dictionary containing a success message indicating that the game
        has been successfully started.

    Raises:
        HTTPException:
            - 404 (Not Found): If the specified game does not exist.
            - 422 (Unprocessable Entity): If there is an issue updating the game
              status or if the data integrity check fails.

    TODO:
        - Assign initial hands and roles to players.
        - Create the initial game deck.
    """
    game_id = game_start_info["game_id"]
    host_name = game_start_info["player_name"]

    # Retrieve game data
    try:
        game = get_full_game(game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Check game data integrity with current game status
    verify_data_start(game, host_name)

    # Update game status to started and assign turn owner and play direction
    new_game_status = GameUpdate(
        state=1, play_direction=True, turn_owner=game.players[0].table_position
    )
    try:
        update_game(game_id, new_game_status)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    # TODO: Assign initial hands and roles to players
    # TODO: Create initial deck

    return {"message": f"Game {game_id} started successfully"}


@router.get("/game/{game_id}")
async def get_game_by_id(game_id: int):
    """
    Get a game by its ID.

    Args:
        game_id (int): The ID of the game to retrieve.

    Returns:
        dict: A JSON response containing the game information.

    Raises:
        HTTPException: If the game does not exist.
    """
    try:
        game = get_game(game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

    game, winner = verify_finished_game(game)

    if winner is not None:
        return {"message": f"Game {game_id} finished successfully", "winner": winner}

    return game