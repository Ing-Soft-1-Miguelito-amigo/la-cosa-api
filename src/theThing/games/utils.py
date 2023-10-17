from fastapi import HTTPException
from pony.orm import ObjectNotFound as ExceptionObjectNotFound
from .crud import get_full_game, update_game, get_game
from .schemas import GameOut, GameInDB, GameUpdate
from ..cards.crud import (
    get_card,
    remove_card_from_player,
    update_card,
    give_card_to_player,
)
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
        raise HTTPException(
            status_code=422, detail="El nombre de la partida no puede ser vacío"
        )

    if not host_name:
        raise HTTPException(
            status_code=422, detail="El nombre del host no puede ser vacío"
        )

    if min_players < 4:
        raise HTTPException(
            status_code=422,
            detail="El mínimo de jugadores no puede ser menor a 4",
        )

    if max_players > 12:
        raise HTTPException(
            status_code=422,
            detail="El máximo de jugadores no puede ser mayor a 12",
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
            status_code=422,
            detail="No hay suficientes jugadores para iniciar la partida",
        )

    if len(game.players) > game.max_players:
        raise HTTPException(
            status_code=422,
            detail="Hay demasiados jugadores para iniciar la partida",
        )

    if host_name not in [player.name for player in game.players]:
        raise HTTPException(
            status_code=422, detail="El host no está dentro de la partida"
        )

    for player in game.players:
        if player.name == host_name:
            if not player.owner:
                raise HTTPException(
                    status_code=422,
                    detail="El jugador provisto no es el host de la partida",
                )
            else:
                break

    if game.state != 0:
        raise HTTPException(
            status_code=422, detail="La partida especificada ya comenzó"
        )


def verify_finished_game(game: GameOut):
    alive_players = [player for player in game.players if player.alive]

    if len(alive_players) == 1 and game.state == 1:
        game.state = 2
        game_id = game.id
        game_new_state = GameUpdate(state=game.state)
        game_updated = update_game(game_id, game_new_state)
        game_updated_id = game_updated.id
        game_out_updated = get_game(game_updated_id)
        return game_out_updated

    return game


def verify_data_play_card(
    game_id: int, player_id: int, card_id: int, destination_name: str
):
    # Verify that the game exists and it is started
    try:
        game = get_full_game(game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=404, detail=str("No se encontró la partida")
        )
    if game.state != 1:
        raise HTTPException(
            status_code=422, detail="La partida aún no ha comenzado"
        )

    # Verify that the player exists, and it is the turn owner and it is alive
    try:
        player = get_player(player_id, game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=422,
            detail=str("No se encontró el jugador especificado"),
        )
    if game.turn_owner != player.table_position or not player.alive:
        raise HTTPException(
            status_code=422, detail="No es el turno del jugador especificado"
        )

    # Verify that the card exists and it is in the player hand
    try:
        card = get_card(card_id, game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=422, detail=str("No se encontró la carta especificada")
        )
    if card not in player.hand or card not in game.deck or card.state == 0:
        raise HTTPException(
            status_code=422,
            detail="La carta no pertenece a la mano del jugador o al mazo de la partida",
        )
    if card.playable is False:
        raise HTTPException(
            status_code=422, detail="La carta seleccionada no es jugable"
        )

    # Get the destination player by his name and check that is not the same player and exists and is alive
    destination_player = None
    for p in game.players:
        if p.name == destination_name:
            destination_player = p
            break
    if destination_player is None:
        raise HTTPException(
            status_code=422, detail="No se encontró al jugador objetivo"
        )
    if destination_player.id == player.id:
        raise HTTPException(
            status_code=422,
            detail="No se puede aplicar el efecto a sí mismo",
        )
    if not destination_player.alive:
        raise HTTPException(
            status_code=422, detail="El jugador objetivo no está vivo"
        )
    alive_players = [p.table_position for p in game.players if p.alive]
    alive_players.sort()
    index_player = alive_players.index(player.table_position)
    index_destination_player = alive_players.index(
        destination_player.table_position
    )
    # check if the destination player is adjacent to the player,
    # the first and the last player are adjacent
    if index_destination_player == (index_player + 1) % len(
        alive_players
    ) or index_destination_player == (index_player - 1) % len(alive_players):
        pass
    else:
        raise HTTPException(
            status_code=422,
            detail="El jugador destino no está sentado en una posición adyacente",
        )
    return game, player, card, destination_player


def play_action_card(
    game: GameInDB,
    player: PlayerBase,
    card: CardBase,
    destination_player: PlayerBase,
):
    match card.code:
        case "lla":  # flamethrower
            if len(player.hand) <= 4:
                raise HTTPException(
                    status_code=404,
                    detail="El jugador tiene menos cartas de las necesarias para jugar",
                )
            card.state = 0
            destination_player.alive = False
            player = remove_card_from_player(card.id, player.id, game.id)
            # check that the player has 4 cards in hand
            pass
        case _:  # other cards
            if len(player.hand) <= 4:
                raise HTTPException(
                    status_code=404,
                    detail="El jugador tiene menos cartas de las necesarias para jugar",
                )
            card.state = 0
            player = remove_card_from_player(card.id, player.id, game.id)
            # check that the player has 4 cards in hand
            # TODO: Implement other cards
            pass

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


def verify_data_discard_card(game_id: int, player_id: int, card_id: int):
    # Verify that the game exists and it is started
    try:
        game = get_full_game(game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(status_code=404, detail="No se encontró la partida")
    if game.state != 1:
        raise HTTPException(
            status_code=422, detail="La partida aún no ha comenzado"
        )
    if game.turn.state != 1:
        raise HTTPException(
            status_code=422, detail="No es posible descartar en este momento"
        )

    # Verify that the player exists, and it is the turn owner, is alive and has already stealed a card.
    try:
        player = get_player(player_id, game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=404, detail="No se encontró el jugador especificado"
        )
    if game.turn_owner != player.table_position or not player.alive:
        raise HTTPException(
            status_code=422, detail="No es el turno del jugador especificado"
        )
    if len(player.hand) <= 4:
        raise HTTPException(
            status_code=422,
            detail="No es posible descartar sin levantar una carta primero",
        )

    # TODO: check the turn status

    # Verify that the card exists and it is in the player hand
    try:
        card = get_card(card_id, game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=404, detail="No se encontró la carta especificada"
        )
    if card not in player.hand or card not in game.deck or card.state == 0:
        raise HTTPException(
            status_code=422,
            detail="La carta no pertenece a la mano del jugador o al mazo de la partida",
        )
    if card.playable is False:
        raise HTTPException(
            status_code=422, detail="La carta seleccionada no es jugable"
        )

    return game, player, card


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


def calculate_winners(game_id: int):
    """
    Calculate the winners of the game.
    PRE: the game exists and it is finished.
    """
    game = get_full_game(game_id)
    players = game.players
    winners = [player.id for player in players if player.alive]

    return winners
