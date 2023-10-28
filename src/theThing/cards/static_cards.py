# Version: 1.0
""" 
This file contains all static cards. The cards are created as a dictionary of
dictionaries. The key is the card code. 
"""

dict_of_cards = {
    # The Thing cards
    "lco": {
        "code": "lco",
        "name": "La Cosa",
        "kind": 5,
        "description": "La Cosa",
        "number_in_card": 0,
        "amount_in_deck": 1,
    },
    # Infected cards
    "inf4": {
        "code": "inf",
        "name": "¡Infectado!",
        "kind": 3,
        "description": "Si recibes esta carta de otro jugador, quedas infectado y debes quedarte esta carta hasta el "
        "final de la partida.",
        "number_in_card": 4,
        "amount_in_deck": 8,
    },
    "inf6": {
        "code": "inf",
        "name": "¡Infectado!",
        "kind": 3,
        "description": "Si recibes esta carta de otro jugador, quedas infectado y debes quedarte esta carta hasta el "
        "final de la partida.",
        "number_in_card": 6,
        "amount_in_deck": 2,
    },
    "inf7": {
        "code": "inf",
        "name": "¡Infectado!",
        "kind": 3,
        "description": "Si recibes esta carta de otro jugador, quedas infectado y debes quedarte esta carta hasta el "
        "final de la partida.",
        "number_in_card": 7,
        "amount_in_deck": 2,
    },
    "inf8": {
        "code": "inf",
        "name": "¡Infectado!",
        "kind": 3,
        "description": "Si recibes esta carta de otro jugador, quedas infectado y debes quedarte esta carta hasta el "
        "final de la partida.",
        "number_in_card": 8,
        "amount_in_deck": 1,
    },
    "inf9": {
        "code": "inf",
        "name": "¡Infectado!",
        "kind": 3,
        "description": "Si recibes esta carta de otro jugador, quedas infectado y debes quedarte esta carta hasta el "
        "final de la partida.",
        "number_in_card": 9,
        "amount_in_deck": 2,
    },
    "inf10": {
        "code": "inf",
        "name": "¡Infectado!",
        "kind": 3,
        "description": "Si recibes esta carta de otro jugador, quedas infectado y debes quedarte esta carta hasta el "
        "final de la partida.",
        "number_in_card": 10,
        "amount_in_deck": 2,
    },
    "inf11": {
        "code": "inf",
        "name": "¡Infectado!",
        "kind": 3,
        "description": "Si recibes esta carta de otro jugador, quedas infectado y debes quedarte esta carta hasta el "
        "final de la partida.",
        "number_in_card": 11,
        "amount_in_deck": 3,
    },
    # ACTION CARDS
    # Flamethrower cards
    "lla4": {
        "code": "lla",
        "name": "Lanzallamas",
        "kind": 0,
        "description": "Elimina de la partida a un jugador adyacente",
        "number_in_card": 4,
        "amount_in_deck": 2,
    },
    "lla6": {
        "code": "lla",
        "name": "Lanzallamas",
        "kind": 0,
        "description": "Elimina de la partida a un jugador adyacente",
        "number_in_card": 6,
        "amount_in_deck": 1,
    },
    "lla9": {
        "code": "lla",
        "name": "Lanzallamas",
        "kind": 0,
        "description": "Elimina de la partida a un jugador adyacente",
        "number_in_card": 9,
        "amount_in_deck": 1,
    },
    "lla11": {
        "code": "lla",
        "name": "Lanzallamas",
        "kind": 0,
        "description": "Elimina de la partida a un jugador adyacente",
        "number_in_card": 11,
        "amount_in_deck": 1,
    },
    # Watch your back cards
    "vte4": {
        "code": "vte",
        "name": "Vigila tus espaldas",
        "kind": 0,
        "description": "Invierte el orden de juego. Ahora, tanto el orden de turnos como los intercambios de cartas van en el sentido contrario",
        "number_in_card": 4,
        "amount_in_deck": 1,
    },
    "vte9": {
        "code": "vte",
        "name": "Vigila tus espaldas",
        "kind": 0,
        "description": "Invierte el orden de juego. Ahora, tanto el orden de turnos como los intercambios de cartas van en el sentido contrario",
        "number_in_card": 9,
        "amount_in_deck": 1,
    },
    # Whisky cards
    "whk4": {
        "code": "whk",
        "name": "Whisky",
        "kind": 0,
        "description": "Muestra todas tus cartas a todos los jugadores. Solo puedes jugar esta carta sobre ti mismo.",
        "number_in_card": 4,
        "amount_in_deck": 1,
    },
    "whk6": {
        "code": "whk",
        "name": "Whisky",
        "kind": 0,
        "description": "Muestra todas tus cartas a todos los jugadores. Solo puedes jugar esta carta sobre ti mismo.",
        "number_in_card": 6,
        "amount_in_deck": 1,
    },
    "whk10": {
        "code": "whk",
        "name": "Whisky",
        "kind": 0,
        "description": "Muestra todas tus cartas a todos los jugadores. Solo puedes jugar esta carta sobre ti mismo.",
        "number_in_card": 10,
        "amount_in_deck": 1,
    },
    # Change places cards
    "cdl4": {
        "code": "cdl",
        "name": "Cambio de lugar",
        "kind": 0,
        "description": "Cambiate de sitio con un jugador adyacente que no esté en cuarentena o tras una puerta "
        "trancada.",
        "number_in_card": 4,
        "amount_in_deck": 2,
    },
    "cdl7": {
        "code": "cdl",
        "name": "Cambio de lugar",
        "kind": 0,
        "description": "Cambiate de sitio con un jugador adyacente que no esté en cuarentena o tras una puerta "
        "trancada.",
        "number_in_card": 7,
        "amount_in_deck": 1,
    },
    "cdl9": {
        "code": "cdl",
        "name": "Cambio de lugar",
        "kind": 0,
        "description": "Cambiate de sitio con un jugador adyacente que no esté en cuarentena o tras una puerta "
        "trancada.",
        "number_in_card": 9,
        "amount_in_deck": 1,
    },
    "cdl11": {
        "code": "cdl",
        "name": "Cambio de lugar",
        "kind": 0,
        "description": "Cambiate de sitio con un jugador adyacente que no esté en cuarentena o tras una puerta "
        "trancada.",
        "number_in_card": 11,
        "amount_in_deck": 1,
    },
    # You'd better run cards
    "mvc4": {
        "code": "mvc",
        "name": "¡Más vale que corras!",
        "kind": 0,
        "description": "Cambiate de sitio con cualquier jugador de tu elección que no esté en Cuarentena, ignorando "
        "cualquier puerta trancada.",
        "number_in_card": 4,
        "amount_in_deck": 2,
    },
    "mvc7": {
        "code": "mvc",
        "name": "¡Más vale que corras!",
        "kind": 0,
        "description": "Cambiate de sitio con cualquier jugador de tu elección que no esté en Cuarentena, ignorando "
        "cualquier puerta trancada.",
        "number_in_card": 7,
        "amount_in_deck": 1,
    },
    "mvc9": {
        "code": "mvc",
        "name": "¡Más vale que corras!",
        "kind": 0,
        "description": "Cambiate de sitio con cualquier jugador de tu elección que no esté en Cuarentena, ignorando "
        "cualquier puerta trancada.",
        "number_in_card": 9,
        "amount_in_deck": 1,
    },
    "mvc11": {
        "code": "mvc",
        "name": "¡Más vale que corras!",
        "kind": 0,
        "description": "Cambiate de sitio con cualquier jugador de tu elección que no esté en Cuarentena, ignorando "
        "cualquier puerta trancada.",
        "number_in_card": 11,
        "amount_in_deck": 1,
    },
    # Suspicion cards
    "sos4": {
        "code": "sos",
        "name": "Sospecha",
        "kind": 0,
        "description": "Mira una carta aleatoria de la mano de un jugador adyacente.",
        "number_in_card": 4,
        "amount_in_deck": 4,
    },
    "sos7": {
        "code": "sos",
        "name": "Sospecha",
        "kind": 0,
        "description": "Mira una carta aleatoria de la mano de un jugador adyacente.",
        "number_in_card": 7,
        "amount_in_deck": 1,
    },
    "sos8": {
        "code": "sos",
        "name": "Sospecha",
        "kind": 0,
        "description": "Mira una carta aleatoria de la mano de un jugador adyacente.",
        "number_in_card": 8,
        "amount_in_deck": 1,
    },
    "sos9": {
        "code": "sos",
        "name": "Sospecha",
        "kind": 0,
        "description": "Mira una carta aleatoria de la mano de un jugador adyacente.",
        "number_in_card": 9,
        "amount_in_deck": 1,
    },
    "sos10": {
        "code": "sos",
        "name": "Sospecha",
        "kind": 0,
        "description": "Mira una carta aleatoria de la mano de un jugador adyacente.",
        "number_in_card": 10,
        "amount_in_deck": 1,
    },
    # Analysis cards
    "ana5": {
        "code": "ana",
        "name": "Análisis",
        "kind": 0,
        "description": "Mira la mano de cartas de un jugador adyacente.",
        "number_in_card": 5,
        "amount_in_deck": 1,
    },
    "ana6": {
        "code": "ana",
        "name": "Análisis",
        "kind": 0,
        "description": "Mira la mano de cartas de un jugador adyacente.",
        "number_in_card": 6,
        "amount_in_deck": 1,
    },
    # Axe cards
    "hac4": {
        "code": "hac",
        "name": "Hacha",
        "kind": 0,
        "description": "Retira una carta 'Puerta trancada' o 'Cuarentena' de tí mismo o de un jugador adyacente",
        "number_in_card": 4,
        "amount_in_deck": 1,
    },
    "hac9": {
        "code": "hac",
        "name": "Hacha",
        "kind": 0,
        "description": "Retira una carta 'Puerta trancada' o 'Cuarentena' de tí mismo o de un jugador adyacente",
        "number_in_card": 9,
        "amount_in_deck": 1,
    },
    # Resolute cards
    "det4": {
        "code": "det",
        "name": "Determinación",
        "kind": 0,
        "description": "Roba 3 cartas 'Aléjate!', elige 1 para quedártela y descarta las demás. A continuación, "
        "juega o descarta 1 carta.",
        "number_in_card": 4,
        "amount_in_deck": 2,
    },
    "det6": {
        "code": "det",
        "name": "Determinación",
        "kind": 0,
        "description": "Roba 3 cartas 'Aléjate!', elige 1 para quedártela y descarta las demás. A continuación, "
        "juega o descarta 1 carta.",
        "number_in_card": 6,
        "amount_in_deck": 1,
    },
    "det9": {
        "code": "det",
        "name": "Determinación",
        "kind": 0,
        "description": "Roba 3 cartas 'Aléjate!', elige 1 para quedártela y descarta las demás. A continuación, "
        "juega o descarta 1 carta.",
        "number_in_card": 9,
        "amount_in_deck": 1,
    },
    "det10": {
        "code": "det",
        "name": "Determinación",
        "kind": 0,
        "description": "Roba 3 cartas 'Aléjate!', elige 1 para quedártela y descarta las demás. A continuación, "
        "juega o descarta 1 carta.",
        "number_in_card": 10,
        "amount_in_deck": 1,
    },
    # Seduction cards
    "sed4": {
        "code": "sed",
        "name": "Seducción",
        "kind": 0,
        "description": "Intercambia una carta con cualquier jugador adyacente que no esté en cuarentena. Tu turno "
        "termina.",
        "number_in_card": 4,
        "amount_in_deck": 2,
    },
    "sed6": {
        "code": "sed",
        "name": "Seducción",
        "kind": 0,
        "description": "Intercambia una carta con cualquier jugador adyacente que no esté en cuarentena. Tu turno "
        "termina.",
        "number_in_card": 6,
        "amount_in_deck": 1,
    },
    "sed7": {
        "code": "sed",
        "name": "Seducción",
        "kind": 0,
        "description": "Intercambia una carta con cualquier jugador adyacente que no esté en cuarentena. Tu turno "
        "termina.",
        "number_in_card": 7,
        "amount_in_deck": 1,
    },
    "sed8": {
        "code": "sed",
        "name": "Seducción",
        "kind": 0,
        "description": "Intercambia una carta con cualquier jugador adyacente que no esté en cuarentena. Tu turno "
        "termina.",
        "number_in_card": 8,
        "amount_in_deck": 1,
    },
    "sed10": {
        "code": "sed",
        "name": "Seducción",
        "kind": 0,
        "description": "Intercambia una carta con cualquier jugador adyacente que no esté en cuarentena. Tu turno "
        "termina.",
        "number_in_card": 10,
        "amount_in_deck": 1,
    },
    "sed11": {
        "code": "sed",
        "name": "Seducción",
        "kind": 0,
        "description": "Intercambia una carta con cualquier jugador adyacente que no esté en cuarentena. Tu turno "
        "termina.",
        "number_in_card": 11,
        "amount_in_deck": 1,
    },
    # DEFENSE CARDS
    # No barbecue! cards
    "ndb4": {
        "code": "ndb",
        "name": "¡Nada de barbacoas!",
        "kind": 1,
        "description": "Cancela una carta 'Lanzallamas' que te tenga como objetivo. Roba 1 carta 'Aléjate!' en "
        "sustitución de esta",
        "number_in_card": 4,
        "amount_in_deck": 1,
    },
    "ndb6": {
        "code": "ndb",
        "name": "¡Nada de barbacoas!",
        "kind": 1,
        "description": "Cancela una carta 'Lanzallamas' que te tenga como objetivo. Roba 1 carta 'Aléjate!' en "
        "sustitución de esta",
        "number_in_card": 6,
        "amount_in_deck": 1,
    },
    "ndb11": {
        "code": "ndb",
        "name": "¡Nada de barbacoas!",
        "kind": 1,
        "description": "Cancela una carta 'Lanzallamas' que te tenga como objetivo. Roba 1 carta 'Aléjate!' en "
        "sustitución de esta",
        "number_in_card": 11,
        "amount_in_deck": 1,
    },
    # I'm comfortable cards
    "aeb4": {
        "code": "aeb",
        "name": "Aquí estoy bien",
        "kind": 1,
        "description": "Cancela una carta '¡Cambio de lugar!' o '¡Más vale que corras!' de la que seas objetivo. Roba "
        "1 carta 'Aléjate!' en sustitución de esta.",
        "number_in_card": 4,
        "amount_in_deck": 1,
    },
    "aeb6": {
        "code": "aeb",
        "name": "Aquí estoy bien",
        "kind": 1,
        "description": "Cancela una carta '¡Cambio de lugar!' o '¡Más vale que corras!' de la que seas objetivo. Roba "
        "1 carta 'Aléjate!' en sustitución de esta.",
        "number_in_card": 6,
        "amount_in_deck": 1,
    },
    "aeb11": {
        "code": "aeb",
        "name": "Aquí estoy bien",
        "kind": 1,
        "description": "Cancela una carta '¡Cambio de lugar!' o '¡Más vale que corras!' de la que seas objetivo. Roba "
        "1 carta 'Aléjate!' en sustitución de esta.",
        "number_in_card": 11,
        "amount_in_deck": 1,
    },
    # Scary cards
    "ate5": {
        "code": "ate",
        "name": "Aterrador",
        "kind": 1,
        "description": "Niégate a un ofrecimiento de intercambio de cartas y mira la carta que te has negado a "
        "recibir. Roba 1 carta 'Aléjate!' en lugar de esta.",
        "number_in_card": 5,
        "amount_in_deck": 1,
    },
    "ate6": {
        "code": "ate",
        "name": "Aterrador",
        "kind": 1,
        "description": "Niégate a un ofrecimiento de intercambio de cartas y mira la carta que te has negado a "
        "recibir. Roba 1 carta 'Aléjate!' en lugar de esta.",
        "number_in_card": 6,
        "amount_in_deck": 1,
    },
    "ate8": {
        "code": "ate",
        "name": "Aterrador",
        "kind": 1,
        "description": "Niégate a un ofrecimiento de intercambio de cartas y mira la carta que te has negado a "
        "recibir. Roba 1 carta 'Aléjate!' en lugar de esta.",
        "number_in_card": 8,
        "amount_in_deck": 1,
    },
    "ate11": {
        "code": "ate",
        "name": "Aterrador",
        "kind": 1,
        "description": "Niégate a un ofrecimiento de intercambio de cartas y mira la carta que te has negado a "
        "recibir. Roba 1 carta 'Aléjate!' en lugar de esta.",
        "number_in_card": 11,
        "amount_in_deck": 1,
    },
    # No, thanks! cards
    "ngs4": {
        "code": "ngs",
        "name": "¡No, gracias!",
        "kind": 1,
        "description": "Niégate a un ofrecimiento de intercambio de cartas. Roba 1 carta 'Aléjate!' en sustitución a "
        "esta.",
        "number_in_card": 4,
        "amount_in_deck": 1,
    },
    "ngs6": {
        "code": "ngs",
        "name": "¡No, gracias!",
        "kind": 1,
        "description": "Niégate a un ofrecimiento de intercambio de cartas. Roba 1 carta 'Aléjate!' en sustitución a "
        "esta.",
        "number_in_card": 6,
        "amount_in_deck": 1,
    },
    "ngs8": {
        "code": "ngs",
        "name": "¡No, gracias!",
        "kind": 1,
        "description": "Niégate a un ofrecimiento de intercambio de cartas. Roba 1 carta 'Aléjate!' en sustitución a "
        "esta.",
        "number_in_card": 8,
        "amount_in_deck": 1,
    },
    "ngs11": {
        "code": "ngs",
        "name": "¡No, gracias!",
        "kind": 1,
        "description": "Niégate a un ofrecimiento de intercambio de cartas. Roba 1 carta 'Aléjate!' en sustitución a "
        "esta.",
        "number_in_card": 11,
        "amount_in_deck": 1,
    },
    # Missed! cards
    "fal4": {
        "code": "fal",
        "name": "¡Fallaste!",
        "kind": 1,
        "description": "El siguiente jugador después de ti realiza el intercambio de cartas en lugar de hacerlo tú. "
        "No queda infectado si reciba una carta '¡Infectado!'. Roba una carta '¡Aléjate!' en "
        "sustitución de esta.",
        "number_in_card": 4,
        "amount_in_deck": 1,
    },
    "fal6": {
        "code": "fal",
        "name": "¡Fallaste!",
        "kind": 1,
        "description": "El siguiente jugador después de ti realiza el intercambio de cartas en lugar de hacerlo tú. "
        "No queda infectado si reciba una carta '¡Infectado!'. Roba una carta '¡Aléjate!' en "
        "sustitución de esta.",
        "number_in_card": 6,
        "amount_in_deck": 1,
    },
    "fal11": {
        "code": "fal",
        "name": "¡Fallaste!",
        "kind": 1,
        "description": "El siguiente jugador después de ti realiza el intercambio de cartas en lugar de hacerlo tú. "
        "No queda infectado si reciba una carta '¡Infectado!'. Roba una carta '¡Aléjate!' en "
        "sustitución de esta.",
        "number_in_card": 11,
        "amount_in_deck": 1,
    },
    # OBSTACLE CARDS
    # Barred door cards
    "pat4": {
        "code": "ptr",
        "name": "Puerta atrancada",
        "kind": 2,
        "description": "Coloca esta carta entre un jugador adyacente y tu. No se permiten acciones entre estos "
        "jugadores y tu.",
        "number_in_card": 4,
        "amount_in_deck": 1,
    },
    "pat7": {
        "code": "ptr",
        "name": "Puerta atrancada",
        "kind": 2,
        "description": "Coloca esta carta entre un jugador adyacente y tu. No se permiten acciones entre estos "
        "jugadores y tu.",
        "number_in_card": 7,
        "amount_in_deck": 1,
    },
    "pat11": {
        "code": "ptr",
        "name": "Puerta atrancada",
        "kind": 2,
        "description": "Coloca esta carta entre un jugador adyacente y tu. No se permiten acciones entre estos "
        "jugadores y tu.",
        "number_in_card": 11,
        "amount_in_deck": 1,
    },
    # Quarantine cards
    "cua5": {
        "code": "cua",
        "name": "Cuarentena",
        "kind": 2,
        "description": "Durante dos rondas, un jugador adyacente debe robar, descartar e intercambiar cartas boca "
        "arriba. No puede eliminar jugadores ni cambiar de sitio.",
        "number_in_card": 5,
        "amount_in_deck": 1,
    },
    "cua9": {
        "code": "cua",
        "name": "Cuarentena",
        "kind": 2,
        "description": "Durante dos rondas, un jugador adyacente debe robar, descartar e intercambiar cartas boca "
        "arriba. No puede eliminar jugadores ni cambiar de sitio.",
        "number_in_card": 9,
        "amount_in_deck": 1,
    },
}
