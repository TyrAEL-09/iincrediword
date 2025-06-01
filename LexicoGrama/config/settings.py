# config/settings.py

class GameSettings:
    """Configuraciones relacionadas con la lógica del juego."""
    GRID_SIZE = (5, 6)
    TARGET_WORDS_COUNT = 7
    WORD_DISTRIBUTION = {9: 1, 8: 1, 7: 1, 6: 2, 5: 2}
    MAX_REPLACEMENTS_PER_SLOT = 100
    MAX_GLOBAL_GENERATION_ATTEMPTS = 10
    MAX_INTERNAL_BOARD_ATTEMPTS = 20
    WORD_FILE = "palabras.txt"
    SAVE_FILE_NAME = "partida_guardada.pkl"


class UISettings:
    """Configuraciones relacionadas con la interfaz de usuario."""
    MAIN_FONT_FAMILY = "Tahoma"
    GRID_LETTER_FONT_SIZE = 22
    UI_FONT_SIZE = 15
    LOGO_MAX_WIDTH = 500
    LOGO_MAX_HEIGHT = 300
    LOGO_PATH = "lexigrama.png"
    ICON_PATH = "icon.png"

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

    SOUND_CORRECT = "correcto2.mp3"
    SOUND_INCORRECT = "roblox_muerte.mp3"
    MUSIC_BACKGROUND = "lofi_sample.mp3"
    SOUND_WINNING = "winning.mp3"

# Instancias de las configuraciones para fácil acceso
GAME_SETTINGS = GameSettings()
UI_SETTINGS = UISettings()
