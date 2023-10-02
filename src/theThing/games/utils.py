from fastapi import HTTPException
from .schemas import GameOut, GameInDB
from src.theThing.cards.crud import give_card_to_player


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
    set_aside_cards = remaining_cards[set_aside_amount:]
    set_aside_cards.append(the_thing_card)

    # shuffle the deck
    import random

    random.shuffle(remaining_cards)

    # assign the cards to the players
    for player in game.players:
        player_cards = set_aside_cards[:4]
        set_aside_cards = set_aside_cards[4:]
        for card in player_cards:
            give_card_to_player(card.id, player.id, game.id)
