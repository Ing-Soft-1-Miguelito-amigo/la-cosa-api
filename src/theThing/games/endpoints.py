from fastapi import APIRouter, HTTPException
from .schemas import GameCreate
from .crud import create_game
from .utils import verify_data

# Create an APIRouter instance for grouping related endpoints
router = APIRouter()


# Endpoint to create a game
@router.post("/game/create", status_code=201)
async def create_new_game(game_data: GameCreate):
    """
    Create a new game with the provided data.

    Parameters:
    - game_data (GameCreate): Data for creating the game, including name, player counts, host, and optional password.

    Returns:
    - dict: A message indicating the successful creation of the game.
    """
    game_name = game_data.name
    min_players = game_data.min_players
    max_players = game_data.max_players

    # Check that name and host are not empty
    verify_data(game_name, min_players, max_players)

    game = GameCreate(name=game_name, min_players=min_players, max_players=max_players)

    # Perform logic to save the game in the database
    try:
        create_game(game)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {"message": f"Game '{game_name}' created successfully"}
