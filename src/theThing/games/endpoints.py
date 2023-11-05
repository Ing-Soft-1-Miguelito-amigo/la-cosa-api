from fastapi import APIRouter, HTTPException
from pony.orm import ObjectNotFound as ExceptionObjectNotFound
from pydantic import BaseModel
from src.theThing.games.socket_handler import (
    send_player_status_to_player,
    send_game_status_to_players,
    send_game_and_player_status_to_players,
    send_discard_event_to_players,
    send_action_event_to_players,
    send_defense_event_to_players,
    send_finished_game_event_to_players,
)
from .crud import create_game, create_game_deck, get_all_games, save_log, get_logs
from .schemas import GameCreate, GameUpdate, GamePlayerAmount
from .utils import *
from ..cards.crud import *
from ..cards.effect_applications import effect_applications
from ..players.crud import create_player, get_player, delete_player
from ..players.schemas import PlayerCreate
from ..turn.crud import create_turn, update_turn
from ..turn.schemas import TurnCreate

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
        "message": f"Partida '{game_name}' creada por '{host_name}' con éxito",
        "game_id": created_game.id,
        "player_id": host_player.id,
    }


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
        raise HTTPException(
            status_code=422, detail="El nombre del jugador no puede ser vacío"
        )

    new_player = PlayerCreate(name=player_name, owner=False)

    # Perform logic to create and save the player in the DB
    try:
        created_player = create_player(new_player, game_id)
    except Exception as e:
        if str(e) == "No se encontró la partida":
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=422, detail=str(e))

    return {
        "message": "El jugador se unió con éxito",
        "player_id": created_player.id,
        "game_id": game_id,
    }


# Endpoint to start a game
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
    new_game_status = GameUpdate(state=1, play_direction=True)
    try:
        update_game(game_id, new_game_status)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Create turn structure
    try:
        create_turn(game_id, 1)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Create the initial game deck
    create_game_deck(game_id, len(game.players))

    # Assign initial hands to players
    game_with_deck = get_full_game(game_id)
    assign_hands(game_with_deck)

    # Send game and player status to all players
    updated_game = get_full_game(game_id)
    await send_game_and_player_status_to_players(updated_game)

    return {"message": f"Partida {game_id} iniciada con éxito"}


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
        raise HTTPException(status_code=422, detail="La entrada no puede ser vacía")

    game_id = steal_data["game_id"]
    player_id = steal_data["player_id"]

    # Verify data integrity
    try:
        verify_data_steal_card(game_id, player_id)
    except Exception as e:
        raise e

    # Perform logic to steal the card
    try:
        card = get_card_from_deck(game_id)
        give_card_to_player(card.id, player_id, game_id)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Change turn state
    try:
        update_turn(game_id, TurnCreate(state=1))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    updated_player = get_player(player_id, game_id)
    await send_player_status_to_player(player_id, updated_player)

    updated_game = get_game(game_id)
    await send_game_status_to_players(game_id, updated_game)

    return {"message": "Carta robada con éxito"}


# Endpoint to play a card
@router.put("/game/play", status_code=200)
async def play_card(play_data: dict):
    """
    Plays a card and Updates the turn structure

    Parameters:
        play_data (dict): A dict containing game_id, player_id(who plays the card), card_id and destination_name.

    Returns:
        dict: A JSON response indicating the success of the card playing.

    Raises:
        HTTPException:
            - 404 (Not Found): If the specified game does not exist.
            - 422 (Unprocessable Entity): If the card cannot be played.
    """
    # Check valid inputs
    if (
        not play_data
        or not play_data["game_id"]
        or not play_data["player_id"]
        or not play_data["card_id"]
        or not play_data["destination_name"]
    ):
        raise HTTPException(status_code=422, detail="La entrada no puede ser vacía")

    game_id = play_data["game_id"]
    player_id = play_data["player_id"]
    card_id = play_data["card_id"]
    destination_name = play_data["destination_name"]

    game, turn_player, card, destination_player = verify_data_play_card(
        game_id, player_id, card_id, destination_name
    )
    # set the card to played
    remove_card_from_player(card_id, player_id, game_id)

    # Update the turn structure
    if card.code == "sed":
        new_turn = TurnCreate(
            played_card=card_id,
            destination_player=destination_name,
            state=3,
            destination_exchange_player=destination_name,
        )
        # Send event description to all players
        await send_action_event_to_players(
            game_id, turn_player, destination_player, card
        )
    else:
        new_turn = TurnCreate(
            played_card=card_id, destination_player=destination_name, state=2
        )

    update_turn(game_id, new_turn)

    player = get_player(player_id, game_id)
    await send_player_status_to_player(player_id, player)

    updated_game = get_game(game_id)
    await send_game_status_to_players(game_id, updated_game)

    message = (
        f"{player.name} jugó {card.name} a {destination_name}, esperando su respuesta"
    )
    try:
        save_log(game_id, message)
    except Exception as e:
        raise e
    await send_action_event_to_players(game_id, message)
    return {"message": "Carta jugada con éxito"}


# Endpoint to discard a card
@router.put("/game/discard", status_code=200)
async def discard_card(discard_data: dict):
    """
    Discard card from the player hand. It updates the state of the turn.

    Parameters:
        discard_data (dict): A dict containing game_id, player_id and card_id.

    Returns:
        dict: A JSON response indicating the success of the card playing.
        socket event: a socket event containing the updated player and
        game status.

    Raises:
        HTTPException:
            - 404 (Not Found): If the specified game, or player, or card
              does not exists.
            - 422 (Unprocessable Entity):
                Multiple possible errors. Description on "detail".
    """
    # Check valid inputs
    if (
        not discard_data
        or not discard_data["game_id"]
        or not discard_data["player_id"]
        or not discard_data["card_id"]
    ):
        raise HTTPException(status_code=422, detail="La entrada no puede ser vacía")

    game_id = discard_data["game_id"]
    player_id = discard_data["player_id"]
    card_id = discard_data["card_id"]

    try:
        game, player, card = verify_data_discard_card(game_id, player_id, card_id)
    except Exception as e:
        raise e

    # Perform logic to discard the card
    try:
        updated_player = remove_card_from_player(card_id, player_id, game_id)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Change turn state
    try:
        update_turn(
            game_id,
            TurnCreate(state=5),  # Has to be 3 in the future
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Send new status via socket
    await send_player_status_to_player(player_id, updated_player)
    updated_game = get_game(game_id)
    await send_game_status_to_players(game_id, updated_game)
    message = f"{updated_player.name} descartó una carta"
    try:
        save_log(game_id, message)
    except Exception as e:
        raise e

    await send_discard_event_to_players(game_id, updated_player.name, message)

    return {"message": "Carta descartada con éxito"}


@router.put("/game/response", status_code=200)
async def respond_to_action_card(response_data: dict):
    """
    Respond to an action card. It has to be requested just after a call to
    /game/play endpoint.
    Parameters:
        response_data (dict): A dict containing game_id, player_id(who is
        the destination_player in play card) and response_card_id.

    Returns:
        dict: A JSON response indicating the success of the event, either if the
        affected player could defend himself or not.

    Raises:
        HTTPException:
            - 404 (Not Found): If the specified game does not exist.
            - 422 (Unprocessable Entity): If the card cannot be played.
    """
    # Check valid inputs
    if (
        not response_data
        or not response_data["game_id"]
        or not response_data["player_id"]
    ):
        raise HTTPException(status_code=422, detail="La entrada no puede ser vacía")

    game_id = response_data["game_id"]
    defending_player_id = response_data["player_id"]
    response_card_id = response_data["response_card_id"]

    # Verify data and recover game, action_card, attacking_player, and defending player
    try:
        (
            game,
            attacking_player,
            defending_player,
            action_card,
        ) = verify_data_response_basic(game_id, defending_player_id)
    except Exception as e:
        raise e

    if response_card_id is None:
        # Apply the effect of the played card. Call the function from the effect_applications dict
        if action_card.code not in effect_applications:
            effect_applications["default"](
                game, attacking_player, defending_player, action_card
            )
        else:
            await effect_applications[action_card.code](
                game, attacking_player, defending_player, action_card
            )
        # Update turn status
        update_turn(game_id, TurnCreate(state=5))  # Has to be 3 in the future
        # Send event description to all players
        message = f"{attacking_player.name} jugó con exito {action_card.name} a {defending_player.name}"
        try:
            save_log(game_id, message)
        except Exception as e:
            raise e
        await send_action_event_to_players(game_id, message)
    else:
        try:
            response_card_id = int(response_card_id)
            # First some routine checks
            response_card = verify_data_response_card(
                game_id, defending_player, response_card_id
            )
            # Discard the response card from the defending player hand, and give him a new one from the deck.
            remove_card_from_player(response_card_id, defending_player_id, game_id)
            new_card = get_card_from_deck(game_id)
            give_card_to_player(new_card.id, defending_player_id, game_id)
        except Exception as e:
            raise e
        # Update turn and add the response_card
        update_turn(
            game_id, TurnCreate(response_card=response_card_id, state=5)
        )  # Has to be 3 in the future
        # Send event description to all players
        message = f"{defending_player.name} se defendio con {response_card.name} a {attacking_player.name}"
        try:
            save_log(game_id, message)
        except Exception as e:
            raise e
        await send_defense_event_to_players(game_id, message)

    # Send the updated states via sockets
    updated_game = get_game(game_id)
    await send_game_status_to_players(game_id, updated_game)

    updated_defending_player = get_player(defending_player_id, game_id)
    await send_player_status_to_player(defending_player_id, updated_defending_player)

    updated_attacking_player = get_player(attacking_player.id, game_id)
    await send_player_status_to_player(attacking_player.id, updated_attacking_player)

    return {"message": "Efecto de jugada aplicado con éxito"}


@router.put("/game/declare-victory")
async def declare_victory(data: dict):
    """
    Get the results of a game when La Cosa declares its victory.

    Parameters:
        data (dict): A dict containing game_id, player_id (player that is calling the endpoint).

    Returns:
        dict: A JSON response containing the game results (message indicating winners and list of winners).
    """
    # Check valid inputs
    if not data or not data["game_id"] or not data["player_id"]:
        raise HTTPException(status_code=422, detail="La entrada no puede ser vacía.")

    game_id = data["game_id"]
    player_id = data["player_id"]

    # Calculate winners
    game_result = calculate_winners_if_victory_declared(game_id, player_id)
    # Update game status to finished
    update_game(game_id, GameUpdate(state=2))
    updated_game = get_game(game_id)
    await send_game_status_to_players(game_id, updated_game)

    return game_result


@router.get("/game/list")
async def get_list_of_games():
    """
    Get a list of games.

    Returns:
        list: A list of JSON responses containing the game information.
    """
    full_list = get_all_games()
    games_to_return = []

    for game in full_list:
        if game.state == 0:
            game_with_amount = GamePlayerAmount(
                name=game.name,
                id=game.id,
                min_players=game.min_players,
                max_players=game.max_players,
                amount_of_players=len(game.players),
            )

            games_to_return.append(game_with_amount)

    return games_to_return


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
    # game = verify_finished_game(game) it breaks when game is not started,
    # when a game is started this endpoint should not be called?

    return game


@router.get("/game/{game_id}/get-logs")
async def get_game_logs(game_id: int):
    """
    Get the logs of a game by its ID.

    Args:
        game_id (int): The ID of the game to retrieve.

    Returns:
        dict: A JSON response containing the game information.

    Raises:
        HTTPException: If the game does not exist.
    """
    try:
        logs = get_logs(game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

    return logs


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

    # order hand by card id

    return player


@router.put("/game/{game_id}/player/{player_id}/leave")
async def leave_game(game_id: int, player_id: int):
    """
    Leave a game.

    Args:
        game_id (int): The ID of the game the player belongs to.
        player_id (int): The ID of the player to retrieve.

    Returns:
        dict: A JSON response containing the player information.

    Raises:
        HTTPException: If the game or player do not exist.
    """
    try:
        game = get_game(game_id)
        if game.state != 0:
            raise HTTPException(status_code=422, detail="La partida ya ha comenzado")
        player = get_player(player_id, game_id)
        if not player.owner:
            delete_player(player_id, game_id)
            response = {
                "message": f"Jugador {player_id} abandonó la partida {game_id} con éxito"
            }
        else:  # delete all players and the game
            # delete_game(game_id) instead of deleting the game update game and set status = 3
            update_game(game_id, GameUpdate(state=3))
            response = {"message": f"Partida {game_id} finalizada por el host"}
    except ExceptionObjectNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    # send game status to players
    game_to_send = get_game(game_id)
    await send_game_status_to_players(game_id, game_to_send)
    return response


@router.put("/turn/finish")
async def finish_turn(finish_data: dict):
    """
    Finish a turn.
    """
    # Check valid inputs
    if not finish_data or not finish_data["game_id"]:
        raise HTTPException(status_code=422, detail="La entrada no puede ser vacía")

    game_id = finish_data["game_id"]

    verify_data_finish_turn(game_id)

    game = get_game(game_id)

    return_data = verify_finished_game(game)

    game = return_data["game"]

    assign_turn_owner(game)
    # send new status via socket
    updated_game = get_game(game_id)

    await send_game_status_to_players(game_id, updated_game)
    response = {"message": "Turno finalizado con éxito"}
    if return_data["winners"] is not None:
        await send_finished_game_event_to_players(game_id, return_data)
        response = {
            "message": "Partida finalizada con éxito",
            "winners": return_data["winners"],
        }
    return response
