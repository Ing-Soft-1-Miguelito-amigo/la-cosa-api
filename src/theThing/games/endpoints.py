from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .schemas import GameCreate, GameUpdate
from ..players.schemas import PlayerCreate
from ..players.crud import create_player, get_player
from ..cards.schemas import CardBase
from ..cards.crud import get_card_from_deck, give_card_to_player
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

    # Retrieve the full game data to get the host player id
    full_game = get_full_game(created_game.id)
    host_player = full_game.players[0]

    return {
        "message": f"Game '{game_name}' created by '{host_name}' successfully",
        "game_id": created_game.id,
        "player_id": host_player.id,
    }


@router.post("/game/start")
async def start_game(game_start_info: dict):
    """
    Start a game with the provided game start information.

    Parameters:
        game_start_info (dict): A dictionary containing game start information.
            It should include the following keys:
            - 'game_id' (int): The unique identifier of the game.
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
    new_game_status = GameUpdate(state=1, play_direction=True, turn_owner=1)
    try:
        update_game(game_id, new_game_status)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    # TODO: Assign initial hands and roles to players
    # TODO: Create initial deck

    return {"message": f"Game {game_id} started successfully"}


# Endpoint to join a player to a game
@router.post("/game/join", status_code=200)
async def join_game(join_info: dict):
    """
    Join a player to a game. It creates a player and join it to the game.

    Parameters:
        join_info (dict): A dictionary containing the game_id and player_name.

    Returns:
        dict: A JSON response indicating the success of the player joining the game.

    Raises:
        HTTPException: If there is an error during player creation or data validation.
    """
    game_id = join_info["game_id"]
    player_name = join_info["player_name"]

    # Check that name is not empty
    if not player_name:
        raise HTTPException(status_code=422, detail="Player name cannot be empty")

    new_player = PlayerCreate(name=player_name, owner=False)

    # Perform logic to create and save the player in the DB
    try:
        created_player = create_player(new_player, game_id)
    except Exception as e:
        if str(e) == "Game not found":
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=422, detail=str(e))

    return {
        "message": "Player joined game successfully",
        "player_id": created_player.id,
    }


# Endpoint to steal a card
@router.put("/game/steal", status_code=200)
async def steal_card(steal_data: dict):
    """
    Steal a card from the game deck.

    Parameters: 
        steal_data (dict): A dict containing game_id and player_id.

    Returns:
        dict: A JSON response indicating the success of the card stealing.

    Raises:
        HTTPException:
            - 404 (Not Found): If the specified game does not exist.
            - 422 (Unprocessable Entity): If the card cannot be stolen.
    """
    # Check valid inputs
    if not steal_data or not steal_data["game_id"] or not steal_data["player_id"]:
        raise HTTPException(
            status_code=422, detail="Input data cannot be empty"
        )
    
    game_id = steal_data["game_id"]
    player_id = steal_data["player_id"]
    
    # Verify that the game exists and it is started
    try:
        game = get_game(game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(status_code=404, detail=str("Game not found"))
    if game.state != 1:
        raise HTTPException(status_code=422, detail="Game has not started yet")
    """
    Then it will be useful 
    if game.turn_owner != player_id:
        raise HTTPException(status_code=422, detail="It is not the player turn") 
    """
    
    # Perform logic to steal the card
    try:
        card = get_card_from_deck(game_id)
        give_card_to_player(card.id, player_id, game_id)
    except Exception as e:
        if str(e) == "Non existent cards in the deck":
            raise HTTPException(status_code=422, detail=str(e))
        else:
            raise HTTPException(status_code=422, detail=str("Player not found"))

    return {"message": "Card stolen successfully"}


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

    # Check if the game is finished
    game, winner = verify_finished_game(game)

    if winner is not None:
        return {"message": f"Game {game_id} finished successfully", "winner": winner}

    return game


@router.get("/game/{game_id}/player/{player_id}")
async def get_player_by_id(game_id: int, player_id: int):
    """
    Get a player by its ID.

    Args:
        game_id (int): The ID of the game the player belongs to.
        player_id (int): The ID of the player to retrieve.

    Returns:
        dict: A JSON response containing the player information.

    Raises:
        HTTPException: If the game or player do not exist.
    """
    try:
        player = get_player(player_id, game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

    return player
