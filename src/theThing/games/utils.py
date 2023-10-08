from fastapi import HTTPException
from pony.orm import ObjectNotFound as ExceptionObjectNotFound
from .crud import get_full_game
from .schemas import GameOut, GameInDB
from ..cards.crud import (
    get_card,
    remove_card_from_player,
    update_card,
    give_card_to_player,
)
from ..cards.schemas import CardBase, CardUpdate
from ..players.crud import get_player, update_player
from ..players.schemas import PlayerBase, PlayerUpdate
from src.theThing.players.websocket_handler import update_player_status


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
    if game.turn_owner != player.table_position or not player.alive:
        raise HTTPException(status_code=422, detail="It is not the player turn")

    # Verify that the card exists and it is in the player hand
    try:
        card = get_card(card_id, game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(status_code=422, detail=str("Card not found"))
    if card not in player.hand or card not in game.deck or card.state == 0:
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
    if destination_player.id == player.id:
        raise HTTPException(
            status_code=422, detail="The destination player cannot be the same player"
        )
    if not destination_player.alive:
        raise HTTPException(
            status_code=422, detail="The destination player is not alive"
        )
    alive_players = [p.table_position for p in game.players if p.alive]
    alive_players.sort()
    index_player = alive_players.index(player.table_position)
    index_destination_player = alive_players.index(destination_player.table_position)
    # check if the destination player is adjacent to the player,
    # the first and the last player are adjacent
    if index_destination_player == (index_player + 1) % len(
        alive_players
    ) or index_destination_player == (index_player - 1) % len(alive_players):
        pass
    else:
        raise HTTPException(
            status_code=422,
            detail="The destination player is not adjacent to the player",
        )
    return game, player, card, destination_player


def play_action_card(
    game: GameInDB, player: PlayerBase, card: CardBase, destination_player: PlayerBase
):
    match card.code:
        case "lla":  # flamethrower
            if len(player.hand) <= 4:
                raise HTTPException(
                    status_code=404, detail="Player has less than minimum cards to play"
                )
            card.state = 0
            destination_player.alive = False
            player = remove_card_from_player(card.id, player.id, game.id)
            # check that the player has 4 cards in hand
            pass
        case _:  # other cards
            if len(player.hand) <= 4:
                raise HTTPException(
                    status_code=404, detail="Player has less than minimum cards to play"
                )
            card.state = 0
            player = remove_card_from_player(card.id, player.id, game.id)
            # check that the player has 4 cards in hand
            # TODO: Implement other cards
            pass

    # push the changes to the database
    updated_card = update_card(CardUpdate(id=card.id, state=card.state), game.id)
    updated_destination_player = update_player_status(
        PlayerUpdate(
            table_position=destination_player.table_position,
            role=destination_player.role,
            alive=destination_player.alive,
            quarantine=destination_player.quarantine,
        ),
        destination_player.id,
        game.id,
    )
    # get the full game again to have the list of players updated
    updated_game = get_full_game(game.id)
    return updated_game


def assign_hands(game: GameInDB):
    """
    Assign the initial hands to the players following the process specified by game rules.

    Parameters:
    - game (GameInDB): The full game data.

    Returns:
    - None
    """
    amount_of_players = len(game.players)
    full_deck = game.deck
    # Remove infection, panic and The Thing cards from the deck
    remaining_cards = [
        card
        for card in full_deck
        if card.kind != 3 and card.kind != 4 and card.kind != 5
    ]
    the_thing_card = [card for card in full_deck if card.kind == 5][0]

    # set aside 4 cards per player - 1
    set_aside_amount = 4 * amount_of_players - 1
    set_aside_cards = remaining_cards[:set_aside_amount]
    set_aside_cards.append(the_thing_card)

    # assign the cards to the players
    for player in game.players:
        player_cards = set_aside_cards[:4]
        set_aside_cards = set_aside_cards[4:]
        for card in player_cards:
            give_card_to_player(card.id, player.id, game.id)
