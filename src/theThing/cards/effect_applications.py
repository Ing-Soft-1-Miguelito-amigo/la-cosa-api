from fastapi import HTTPException
from pony.orm import ObjectNotFound as ExceptionObjectNotFound
from src.theThing.games.crud import get_full_game, update_game, get_game
from src.theThing.games.schemas import GameOut, GameInDB, GameUpdate
from src.theThing.cards.crud import (
    get_card,
    remove_card_from_player,
    update_card,
    give_card_to_player,
)
from src.theThing.cards.schemas import CardBase, CardUpdate
from src.theThing.players.crud import get_player, update_player
from src.theThing.players.schemas import PlayerBase, PlayerUpdate


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
def apply_flamethrower(game: GameInDB, player: PlayerBase, destination_player: PlayerBase, card: CardBase):
    # check that the player has 4 cards in hand
    card.state = 0
    destination_player.alive = False
    player = remove_card_from_player(card.id, player.id, game.id)

    # push the changes to the database
    updated_card = update_card(
        CardUpdate(id=card.id, state=card.state), game.id
    )
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


def just_discard(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase):
    # other cards
    card.state = 0
    player = remove_card_from_player(card.id, player.id, game.id)

    # push the changes to the database
    updated_card = update_card(
        CardUpdate(id=card.id, state=card.state), game.id
    )


effect_applications = {
    "lla": apply_flamethrower,
    "default": just_discard,
}
