from fastapi import HTTPException
from pony.orm import ObjectNotFound as ExceptionObjectNotFound
from .crud import get_full_game
from .schemas import GameOut, GameInDB
from ..cards.crud import get_card, remove_card_from_player, update_card
from ..cards.schemas import CardBase, CardUpdate
from ..players.crud import get_player, update_player
from ..players.schemas import PlayerBase, PlayerUpdate


# Function to verify configuration data integrity
def verify_data_create(game_name, min_players, max_players, host_name):
    """
    Verify the integrity of game configuration data.

    Parameters:
    - game_name (str): The name of the game.
    - min_players (int): The minimum number of players.
    - max_players (int): The maximum number of players.
    - host_name (str): The name of the host.

    Raises:
    - HTTPException (status_code=422): If game or host name is empty, or if min_players is less than 4 or max_players
    is greater than 12.

    Returns:
    - None
    """
    if not game_name:
        raise HTTPException(status_code=422, detail="Game name cannot be empty")

    if not host_name:
        raise HTTPException(status_code=422, detail="Host name cannot be empty")

    if min_players < 4:
        raise HTTPException(
            status_code=422, detail="Minimum players cannot be less than 4"
        )

    if max_players > 12:
        raise HTTPException(
            status_code=422, detail="Maximum players cannot be greater than 12"
        )


# Function to verify configuration data integrity
def verify_data_start(game: GameOut, host_name: str):
    """
    Verify the integrity of game configuration data.

    Parameters:
    - game_id (int): The ID of the game to join.
    - player_name (str): The name of the player.

    Raises:
    - HTTPException (status_code=422): If game or host name is empty, or if min_players is less than 4 or max_players
    is greater than 12.

    Returns:
    - None
    """
    if len(game.players) < game.min_players:
        raise HTTPException(
            status_code=422, detail="Not enough players to start the game"
        )

    if len(game.players) > game.max_players:
        raise HTTPException(
            status_code=422, detail="Too many players to start the game"
        )

    if host_name not in [player.name for player in game.players]:
        raise HTTPException(status_code=422, detail="The host is not in the game")

    for player in game.players:
        if player.name == host_name:
            if not player.owner:
                raise HTTPException(
                    status_code=422,
                    detail="The player provided is not the host of the game",
                )
            else:
                break

    if game.state != 0:
        raise HTTPException(status_code=422, detail="The game has already started")


def verify_finished_game(game: GameOut):
    alive_players = [player for player in game.players if player.alive]

    if len(alive_players) == 1 and game.state == 1:
        game.state = 2
        winner = alive_players[0].name

        return game, winner

    return game, None


def verify_data_play_card(
    game_id: int, player_id: int, card_id: int, destination_name: str
):
    # Verify that the game exists and it is started
    try:
        game = get_full_game(game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(status_code=404, detail=str("Game not found"))
    if game.state != 1:
        raise HTTPException(status_code=422, detail="Game has not started yet")

    # Verify that the player exists, and it is the turn owner and it is alive
    try:
        player = get_player(player_id, game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(status_code=422, detail=str("Player not found"))
    if game.turn_owner != player_id or not player.alive:
        raise HTTPException(status_code=422, detail="It is not the player turn")

    # Verify that the card exists and it is in the player hand
    try:
        card = get_card(card_id, game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(status_code=422, detail=str("Card not found"))
    if card not in player.hand and card not in game.deck and card.state == 0:
        raise HTTPException(
            status_code=422, detail="The card is not in the player hand or in the deck"
        )
    if card.playable is False:
        raise HTTPException(status_code=422, detail="The card is not playable")

    # Get the destination player by his name and check that is not the same player and exists and is alive
    destination_player = None
    for p in game.players:
        if p.name == destination_name:
            destination_player = p
            break
    if destination_player is None:
        raise HTTPException(status_code=422, detail="Destination player not found")
    if destination_player == player:
        raise HTTPException(
            status_code=422, detail="The destination player cannot be the same player"
        )
    return game, player, card, destination_player


def play_action_card(game: GameInDB, player: PlayerBase, card: CardBase, destination_player: PlayerBase):
    match card.code:
        case "lla":  # flamethrower
            card.state = 0
            destination_player.alive = False
            player = remove_card_from_player(card.id, player.id, game.id)
            # check that the player has 4 cards in hand
            if len(player.hand) != 4:
                raise HTTPException(status_code=404, detail="Player has less than 4 cards")
            pass
        case _:  # other cards
            # TODO: Implement other cards
            pass

    # push the changes to the database
    updated_card = update_card(CardUpdate(id=card.id, state=card.state), game.id)
    updated_player = update_player(PlayerUpdate(id=player.id, alive=player.alive), game.id)
    # get the full game again to have the list of players updated
    updated_game = get_full_game(game.id)

    return updated_game
