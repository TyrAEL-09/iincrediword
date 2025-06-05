# settings.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RECURSOS_DIR_GENERAL = BASE_DIR.parent / "recursos"

class GameSettings:
    """Configuraciones relacionadas con la lógica del juego."""
    GRID_SIZE = (5, 6)
    TARGET_WORDS_COUNT = 7
    WORD_DISTRIBUTION = {9: 1, 8: 1, 7: 1, 6: 2, 5: 2}
    MAX_REPLACEMENTS_PER_SLOT = 100
    MAX_GLOBAL_GENERATION_ATTEMPTS = 30
    MAX_INTERNAL_BOARD_ATTEMPTS = 20
    WORD_FILE = BASE_DIR / "palabras.txt"
    
    SAVES_DIR = BASE_DIR / "saves" 
    SAVE_FILE_NAME = SAVES_DIR / "partidas_guardadas.json"


class UISettings:
    """Configuraciones relacionadas con la interfaz de usuario."""
    MAIN_FONT_FAMILY = "Tahoma"
    GRID_LETTER_FONT_SIZE = 22
    UI_FONT_SIZE = 15
    LOGO_MAX_WIDTH = 500
    LOGO_MAX_HEIGHT = 300
    
    # Rutas construidas usando RECURSOS_DIR_GENERAL
    LOGO_PATH = RECURSOS_DIR_GENERAL / "lexigrama.png"
    ICON_PATH = RECURSOS_DIR_GENERAL / "icon.png"

    # Colores utilizados en la interfaz
    COLORS = {
        'bg': "#0a0b29",
        'fg': "#FFFFFF",
        'grid': "#1970a5",
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
    _SOUND_WINNING_FILENAME = "level-win-6416.mp3"

    # Rutas completas a los sonidos
    SOUND_CORRECT = RECURSOS_DIR_GENERAL / _SOUND_CORRECT_FILENAME
    SOUND_INCORRECT = RECURSOS_DIR_GENERAL / _SOUND_INCORRECT_FILENAME
    MUSIC_BACKGROUND = RECURSOS_DIR_GENERAL / _MUSIC_BACKGROUND_FILENAME
    SOUND_WINNING = RECURSOS_DIR_GENERAL / _SOUND_WINNING_FILENAME 

# Instancias de las configuraciones para fácil acceso
GAME_SETTINGS = GameSettings()
UI_SETTINGS = UISettings()
