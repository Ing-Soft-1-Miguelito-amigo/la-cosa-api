from src.theThing.games.crud import *
from src.theThing.cards.crud import *
from src.theThing.players.crud import *


async def apply_cac(
    data: dict,
):
    game = get_game(data["game_id"])
    card = get_card(data["card_id"], game.id)
    player = get_player(data["player_id"], game.id)
    panic_card = get_card(data["panic_card_id"], game.id)

    update_card(CardUpdate(id=data["panic_card_id"], state=0), game.id)

    # Get a new card from the deck
    new_card = get_card_from_deck(game.id)
    while new_card.kind == 4:
        update_card(CardUpdate(id=new_card.id, state=0), game.id)
        new_card = get_card_from_deck(game.id)
    give_card_to_player(new_card.id, player.id, game.id)

    # Return the card to the deck
    remove_card_from_player(card.id, player.id, game.id)

    updated_game = get_full_game(game.id)
    updated_player = get_player(player.id, game.id)
    return updated_player, updated_game
