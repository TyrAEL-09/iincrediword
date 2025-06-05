"""
Módulo principal del Juego de Hexágonos

Este paquete contiene toda la lógica del juego, incluyendo:
- Gestión del estado del juego
- Lógica de palabras y letras
- Elementos de interfaz de usuario
- Animaciones y efectos visuales
"""

# Importa las clases y funciones principales del juego para facilitar su uso en otros módulos.
from Hexa_Link.game.main_game import HexGame           # Clase principal del juego, controla el bucle y la UI.
from Hexa_Link.game.game_state import GameState        # Estado del juego: letras, palabras, puntaje, etc.
from Hexa_Link.game.animations import FireAnimation    # Animación de fuego para combos.
from Hexa_Link.game.word_logic import cargar_pals, elegir  # Lógica de palabras y letras.
from Hexa_Link.game.ui_elements import (
    hexagon_points,        # Calcula los puntos de un hexágono (para dibujar).
    is_over_hexagon,       # Detecta si el mouse está sobre un hexágono.
    draw_hexagons,         # Dibuja los hexágonos del tablero.
    draw_buttons,          # Dibuja los botones de la UI.
    draw_sidebar,          # Dibuja la barra lateral con palabras encontradas.
    draw_pal_actual,     # Dibuja la palabra actual que el usuario está formando.
    draw_score,            # Dibuja el puntaje actual.
    draw_combo_message,    # Dibuja el mensaje de combo si está activo.
    draw_time,             # Dibuja el tiempo transcurrido.
    draw_word_count,       # Dibuja el contador de palabras encontradas/objetivo.
    draw_victory_message   # Dibuja el mensaje de victoria.
)

# Exporta los elementos principales para facilitar las importaciones desde otros módulos.
__all__ = [
    'HexGame',
    'GameState',
    'FireAnimation',
    'cargar_pals',
    'elegir',
    'hexagon_points',
    'is_over_hexagon',
    'draw_hexagons',
    'draw_buttons',
    'draw_sidebar',
    'draw_pal_actual',
    'draw_score',
    'draw_combo_message',
    'draw_time',
    'draw_word_count',
    'draw_victory_message'
]
