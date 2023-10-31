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
from ..turn.crud import update_turn
from ..turn.schemas import TurnCreate
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

    if min_players > max_players:
        raise HTTPException(
            status_code=422,
            detail="El mínimo de jugadores no puede ser mayor al máximo",
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
    winners = None
    reason = None
    turn_owner_name = [player.name for player in game.players if player.table_position == game.turn.owner][0]
    the_thing = [player for player in game.players if player.role == 3][0]
    if game.turn.played_card.code == "lla" and game.turn.response_card is None and game.turn.destination_player == the_thing.name:
        # if a flamethrower was played and killed "La cosa", the game ends and all alive humans win
        game.state = 2
        game_id = game.id
        game_new_state = GameUpdate(state=game.state)
        game = update_game(game_id, game_new_state)
        winners = [player for player in game.players if (player.role == 1 and player.alive)]
        reason = "La cosa fue eliminada por " + turn_owner_name + " ganaron todos los humanos vivos"

    amount_infected_players = len([player for player in game.players if (player.role == 2 and player.alive)])
    if amount_infected_players == len(game.players)-1:
        # if "La cosa" infected all players, the game ends and "La cosa" wins
        game.state = 2
        game_id = game.id
        game_new_state = GameUpdate(state=game.state)
        game = update_game(game_id, game_new_state)
        winners = [player for player in game.players if (player.role == 3 and player.alive)]
        reason = "La cosa infectó a todos los jugadores y gano la partida"

    return_data = {
        "game": game,
        "winners": winners,
        "reason": reason
    }
    return return_data


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
    if game.turn.owner != player.table_position or not player.alive:
        raise HTTPException(
            status_code=422, detail="No es el turno del jugador especificado"
        )
    if game.turn.state != 1:
        raise HTTPException(
            status_code=422,
            detail="El jugador todavia no puede jugar en este turno",
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
    if card.kind not in [0, 2]:
        raise HTTPException(
            status_code=422, detail="No puedes jugar esta carta"
        )
    if card.playable is False:
        raise HTTPException(
            status_code=422, detail="La carta seleccionada no es jugable"
        )
    if len(player.hand) <= 4:
        raise HTTPException(
            status_code=422,
            detail="El jugador tiene menos cartas de las necesarias para jugar",
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
    if destination_player.id == player.id and card.code not in ["whk", "vte"]:
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
    if card.code not in ["mvc", "whk", "vte"]:
        # check if the destination !=player is adjacent to the player,
        # the first and the last player are adjacent
        if index_destination_player == (index_player + 1) % len(
            alive_players
        ) or index_destination_player == (index_player - 1) % len(
            alive_players
        ):
            pass
        else:
            raise HTTPException(
                status_code=422,
                detail="El jugador destino no está sentado en una posición adyacente",
            )
    return game, player, card, destination_player


def verify_data_steal_card(game_id: int, player_id: int):
    # Verify that the game exists and it is started
    try:
        game = get_game(game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=404, detail=str("No se encontró la partida")
        )
    if game.state != 1:
        raise HTTPException(
            status_code=422, detail="La partida aún no ha comenzado"
        )
    if game.turn.state != 0:
        raise HTTPException(
            status_code=422,
            detail="No es posible robar una carta en este momento",
        )

    # Check valid player status
    try:
        player = get_player(player_id, game_id)
        if len(player.hand) >= 5:
            raise HTTPException(
                status_code=422, detail="La mano del jugador está llena"
            )
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=422, detail=str("No se encontró el jugador")
        )

    # Verify that it actually is the player turn
    if game.turn.owner != player.table_position:
        raise HTTPException(status_code=422, detail="No es tu turno")


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
    if game.turn.owner != player.table_position or not player.alive:
        raise HTTPException(
            status_code=422, detail="No es el turno del jugador especificado"
        )
    if len(player.hand) <= 4:
        raise HTTPException(
            status_code=422,
            detail="No es posible descartar sin robar una carta primero",
        )

    # Verify that the card exists and it is in the player hand
    try:
        card = get_card(card_id, game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=404, detail="No se encontró la carta especificada"
        )
    if card.kind == 5:
        raise HTTPException(
            status_code=422, detail="No es posible descartar esta carta"
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


def verify_data_response_basic(game_id: int, defending_player_id: int):
    # It also returns the game, the attacking player, the defending player and the action card
    # Game checks
    try:
        game = get_full_game(game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(status_code=404, detail="No se encontró la partida")
    if game.state != 1:
        raise HTTPException(
            status_code=422, detail="La partida aún no ha comenzado"
        )
    if game.turn.state != 2:
        raise HTTPException(
            status_code=422, detail="No es posible defenderse en este momento"
        )

    # Check if the attacking player exists and its alive
    for player in game.players:
        if player.table_position == game.turn.owner:
            attacking_player = player
            break
    if attacking_player is None:
        raise HTTPException(
            status_code=404, detail="No se encontró el jugador atacante"
        )
    if not attacking_player.alive:
        raise HTTPException(
            status_code=422, detail="El jugador atacante está muerto"
        )
    # Check the defending player exists and its alive
    try:
        defending_player = get_player(defending_player_id, game_id)
    except Exception as e:
        raise HTTPException(
            status_code=404, detail="No se encontró el jugador destino"
        )

    # Check the action card state
    try:
        action_card = get_card(game.turn.played_card.id, game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=404,
            detail="No se encontró la carta de ataque especificada",
        )
    if action_card.state != 0:
        raise HTTPException(
            status_code=422, detail="La carta de ataque no ha sido jugada"
        )

    return game, attacking_player, defending_player, action_card


def verify_data_response_card(
    game_id: int, defending_player: PlayerBase, response_card_id: int
):
    # It also returns the response card
    # Get defense card
    try:
        response_card = get_card(response_card_id, game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=404,
            detail="No se encontró la carta de defensa especificada",
        )
    if response_card.kind != 1:
        raise HTTPException(
            status_code=422, detail="No te puedes defender con esta carta"
        )
    # Player checks
    if len(defending_player.hand) != 4:
        raise HTTPException(
            status_code=422,
            detail="El jugador tiene menos o más de 4 cartas en su mano. Debería tener 4.",
        )
    if response_card not in defending_player.hand:
        raise HTTPException(
            status_code=404,
            detail="La carta de defensa no está en la mano del jugador",
        )
    return response_card


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

        # assign corresponding role
        if len([card for card in player_cards if card.kind == 5]) > 0:
            update_player(PlayerUpdate(role=3), player.id, game.id)
        else:
            update_player(PlayerUpdate(role=1), player.id, game.id)

        for card in player_cards:
            give_card_to_player(card.id, player.id, game.id)


def calculate_winners(game_id: int):
    """
    Calculate the winners of the game.
    PRE: the game exists and it is finished.
    """
    game = get_full_game(game_id)
    players = game.players
    winners = [player.name for player in players if player.alive]

    return winners


def verify_data_finish_turn(game_id: int):
    """
    Verify the integrity of finish turn data.
    """

    # Verify that the game exists and it is started
    try:
        game = get_game(game_id)
    except ExceptionObjectNotFound as e:
        raise HTTPException(
            status_code=404, detail=str("No se encontró la partida")
        )

    if game.state != 1:
        raise HTTPException(
            status_code=422, detail="La partida aún no ha comenzado"
        )

    if game.turn.state != 5:
        raise HTTPException(
            status_code=422, detail="El turno aún no ha terminado"
        )

    return game


def assign_turn_owner(game: GameOut):
    played_card = game.turn.played_card
    if played_card is not None:
        # If played_card is None, then it was discarded, and we need to skip this section
        played_card_code = played_card.code
        response_card = game.turn.response_card
        if (
            played_card_code == "cdl" or played_card_code == "mvc"
        ) and response_card is None:
            # If the played card is "cdl" or "mvc" and there's no response, the turn
            # owner is in the same position of the last turn played.
            update_turn(
                game.id,
                TurnCreate(
                    state=0,
                    played_card=None,
                    response_card=None,
                    destination_player="",
                ),
            )
            return

    # Assign new turn owner, must be an alive player
    # if play direction is clockwise, turn owner is the next player. If not, the previous player
    alive_players = [
        player.table_position for player in game.players if player.alive
    ]
    alive_players.sort()
    if game.play_direction:
        new_turn_owner = alive_players[
            (alive_players.index(game.turn.owner) + 1) % len(alive_players)
        ]
        update_turn(
            game.id,
            TurnCreate(
                owner=new_turn_owner,
                state=0,
                played_card=None,
                response_card=None,
                destination_player="",
            ),
        )
    else:
        new_turn_owner = alive_players[
            (alive_players.index(game.turn.owner) - 1) % len(alive_players)
        ]
        update_turn(
            game.id,
            TurnCreate(
                owner=new_turn_owner,
                state=0,
                played_card=None,
                response_card=None,
                destination_player="",
            ),
        )
