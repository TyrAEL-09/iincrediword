# settings.py
from pathlib import Path # AÑADIDO

BASE_DIR = Path(__file__).resolve().parent.parent # AÑADIDO: Apunta a lexigrama_game
RECURSOS_DIR_GENERAL = BASE_DIR.parent / "recursos" # AÑADIDO: Apunta a content/recursos

class GameSettings:
    """Configuraciones relacionadas con la lógica del juego."""
    GRID_SIZE = (5, 6)
    TARGET_WORDS_COUNT = 7
    WORD_DISTRIBUTION = {9: 1, 8: 1, 7: 1, 6: 2, 5: 2}
    MAX_REPLACEMENTS_PER_SLOT = 100
    MAX_GLOBAL_GENERATION_ATTEMPTS = 10
    MAX_INTERNAL_BOARD_ATTEMPTS = 20
    WORD_FILE = BASE_DIR / "palabras.txt" # MODIFICADO: Ruta absoluta
    
    SAVES_DIR = BASE_DIR / "saves" # AÑADIDO
    SAVE_FILE_NAME = SAVES_DIR / "partidas_guardadas.json" # MODIFICADO: Ruta absoluta


class UISettings:
    """Configuraciones relacionadas con la interfaz de usuario."""
    MAIN_FONT_FAMILY = "Tahoma"
    GRID_LETTER_FONT_SIZE = 22
    UI_FONT_SIZE = 15
    LOGO_MAX_WIDTH = 500
    LOGO_MAX_HEIGHT = 300
    
    # Rutas construidas usando RECURSOS_DIR_GENERAL
    LOGO_PATH = RECURSOS_DIR_GENERAL / "lexigrama.png" # MODIFICADO
    ICON_PATH = RECURSOS_DIR_GENERAL / "icon.png" # MODIFICADO (asegúrate que "icon.png" exista en content/recursos)

    COLORS = {
        'bg': "#1a1a1a",
        'fg': "#FFFFFF",
        'grid': "#333333",
        'grid_fg': "#FFFFFF",
        'button_bg': "#464646",
        'button_fg': "#FFFFFF",
        'found_word_fg': "#F2FF00",
        'hint_fg': "#A0A0A0",
        'selected_cell_bg': "#FFA500",
        'hint_box_bg': "#2a2a2a",
        'hint_box_fg': "#FFFFFF",
        'hint_box_border': "#444444",
        'message_fg': "#FFC107",
        'pause_overlay_bg': "rgba(0, 0, 0, 0.7)",
        'pause_fg': "#FFFFFF"
    }

    # Nombres de archivo originales para sonidos
    _SOUND_CORRECT_FILENAME = "correcto2.mp3"
    _SOUND_INCORRECT_FILENAME = "roblox_muerte.mp3"
    _MUSIC_BACKGROUND_FILENAME = "lofi_sample.mp3"
    _SOUND_WINNING_FILENAME = "winning.mp3"

    # Rutas completas a los sonidos
    SOUND_CORRECT = RECURSOS_DIR_GENERAL / _SOUND_CORRECT_FILENAME # MODIFICADO
    SOUND_INCORRECT = RECURSOS_DIR_GENERAL / _SOUND_INCORRECT_FILENAME # MODIFICADO
    MUSIC_BACKGROUND = RECURSOS_DIR_GENERAL / _MUSIC_BACKGROUND_FILENAME # MODIFICADO
    SOUND_WINNING = RECURSOS_DIR_GENERAL / _SOUND_WINNING_FILENAME # MODIFICADO

# Instancias de las configuraciones para fácil acceso
GAME_SETTINGS = GameSettings()
UI_SETTINGS = UISettings()
