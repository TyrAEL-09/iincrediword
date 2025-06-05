# main.py
import pygame
from .game.lexigrama_game import LexigramaGame
from .config.settings import GAME_SETTINGS, UI_SETTINGS

def main(username: str): 
    game = LexigramaGame(
        username=username, 
        archivo_palabras=GAME_SETTINGS.WORD_FILE, # Esta ya será una ruta Path
        logo_path=UI_SETTINGS.LOGO_PATH, # Esta ya será una ruta Path
        game_settings=GAME_SETTINGS,
        ui_settings=UI_SETTINGS
    )
    game.run()

if __name__ == "__main__":
    # Esta parte es para ejecución directa, necesitará un username de prueba
    # En el flujo normal, main() será llamado desde lexigrama.py con el username
    test_username = "jugador_prueba" 
    print(f"Ejecutando Lexigrama directamente con usuario de prueba: {test_username}")
    main(test_username)
