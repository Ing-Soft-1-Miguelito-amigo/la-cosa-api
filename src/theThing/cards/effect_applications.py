import random
from src.theThing.games.crud import get_full_game, update_game, get_game
from src.theThing.games.schemas import GameInDB, GameUpdate, GameOut
from src.theThing.cards.crud import (
    remove_card_from_player,
    update_card,
    get_card,
)
from src.theThing.cards.schemas import CardBase, CardUpdate
from src.theThing.players.crud import get_player, update_player
from src.theThing.players.schemas import PlayerBase, PlayerUpdate
from src.theThing.games import socket_handler as sh
from src.theThing.turn.schemas import TurnCreate, TurnOut
from src.theThing.turn.crud import create_turn, update_turn
from src.theThing.games.utils import get_player_in_next_n_places

""" 
This file contains the functions to apply the effect of the cards. 
The functions are in a dictionary, which key is the card code. 
IMPORTANT: The parameters must be passed in the following order and types:
    - game: GameInDB
    - player: PlayerBase
    - destination_player: PlayerBase
    - card: CardBase
"""


# Functions implementation
async def apply_flamethrower(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    # check that the player has 4 cards in hand
    card.state = 0
    destination_player.alive = False
    player = remove_card_from_player(card.id, player.id, game.id)

    # push the changes to the database
    updated_card = update_card(CardUpdate(id=card.id, state=card.state), game.id)
    updated_destination_player = update_player(
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


async def apply_vte(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    # Remove the card played from the player
    remove_card_from_player(card.id, player.id, game.id)

    # Invert the game play direction
    new_direction = not game.play_direction
    update_game(game.id, GameUpdate(play_direction=new_direction))

    game = get_game(game.id)
    # get the new destination for exchange
    new_exchange_destination = get_player_in_next_n_places(
        game, destination_player.table_position, 1
    )
    new_turn = TurnCreate(
        destination_player_exchange=new_exchange_destination.name
    )
    update_turn(game.id, new_turn)
    updated_game = get_full_game(game.id)
    return updated_game


async def apply_cdl(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0
    # swap table position between the players
    player.table_position, destination_player.table_position = (
        destination_player.table_position,
        player.table_position,
    )
    # push the changes to the database
    updated_card = update_card(CardUpdate(id=card.id, state=card.state), game.id)

    updated_player = update_player(
        PlayerUpdate(table_position=player.table_position), player.id, game.id
    )

    updated_destination_player = update_player(
        PlayerUpdate(table_position=destination_player.table_position),
        destination_player.id,
        game.id,
    )
    new_turn = TurnCreate(
        owner=updated_player.table_position,
        played_card=card.id,
        destination_player=destination_player.name,
    )
    update_turn(game.id, new_turn)
    updated_game = get_full_game(game.id)
    return updated_game


async def apply_mvc(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0
    # swap table position between the players
    player.table_position, destination_player.table_position = (
        destination_player.table_position,
        player.table_position,
    )
    # push the changes to the database
    updated_card = update_card(CardUpdate(id=card.id, state=card.state), game.id)

    updated_player = update_player(
        PlayerUpdate(table_position=player.table_position), player.id, game.id
    )

    updated_destination_player = update_player(
        PlayerUpdate(table_position=destination_player.table_position),
        destination_player.id,
        game.id,
    )

    new_turn = TurnCreate(
        owner=updated_player.table_position,
        played_card=card.id,
        destination_player=destination_player.name,
    )
    update_turn(game.id, new_turn)
    updated_game = get_full_game(game.id)
    return updated_game


async def apply_ana(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0
    destination_hand = destination_player.hand

    update_card(CardUpdate(id=card.id, state=card.state), game.id)
    await sh.send_analysis_to_player(
        player.id, destination_hand, destination_player.name
    )
    updated_game = get_full_game(game.id)
    return updated_game


async def apply_sos(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0
    destination_card = random.choice(destination_player.hand)

    update_card(CardUpdate(id=card.id, state=card.state), game.id)
    await sh.send_suspicion_to_player(
        player.id, destination_card, destination_player.name
    )
    updated_game = get_full_game(game.id)
    return updated_game


async def apply_whk(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0
    player_hand = player.hand

    update_card(CardUpdate(id=card.id, state=card.state), game.id)
    await sh.send_whk_to_player(game.id, player.name, player_hand)

    updated_game = get_full_game(game.id)
    return updated_game


async def just_discard(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    # other cards
    card.state = 0
    player = remove_card_from_player(card.id, player.id, game.id)

    # push the changes to the database
    updated_card = update_card(CardUpdate(id=card.id, state=card.state), game.id)


effect_applications = {
    "lla": apply_flamethrower,
    "vte": apply_vte,
    "cdl": apply_cdl,
    "mvc": apply_mvc,
    "ana": apply_ana,
    "sos": apply_sos,
    "whk": apply_whk,
    "default": just_discard,
}


async def apply_ate(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0

    # push the changes to the database
    updated_card = update_card(
        CardUpdate(id=card.id, state=card.state), game.id
    )

    card_to_send = player.card_to_exchange
    update_player(PlayerUpdate(card_to_exchange=None), player.id, game.id)

    update_turn(game.id, TurnCreate(state=5))
    await sh.send_ate_to_player(
        game.id, player, destination_player, card_to_send
    )
    # TODO: SEND DEFENSE EVENT TO CLIENT
    updated_game = get_full_game(game.id)
    return updated_game


async def apply_ngs(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0

    # push the changes to the database
    updated_card = update_card(
        CardUpdate(id=card.id, state=card.state), game.id
    )

    update_player(PlayerUpdate(card_to_exchange=None), player.id, game.id)

    update_turn(game.id, TurnCreate(state=5))
    # TODO: SEND DEFENSE EVENT TO CLIENT
    updated_game = get_full_game(game.id)
    return updated_game


async def apply_fal(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0

    # push the changes to the database
    updated_card = update_card(
        CardUpdate(id=card.id, state=card.state), game.id
    )

    update_player(PlayerUpdate(card_to_exchange=None), destination_player.id, game.id)

    game = get_game(game.id)
    new_dest = get_player_in_next_n_places(
        game, destination_player.table_position, 1
    )
    update_turn(
        game.id, TurnCreate(state=4, destination_player_exchange=new_dest.name)
    )
    # TODO: SEND DEFENSE EVENT TO CLIENT


exchange_defense = {
    "ate": apply_ate,
    "ngs": apply_ngs,
    "fal": apply_fal,
    "default": just_discard,
}
