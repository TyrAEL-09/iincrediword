# main.py
import pygame
from game.boggle_game import BoggleGame
from config.settings import GAME_SETTINGS, UI_SETTINGS

def main():
    pygame.mixer.init() # Inicializa Pygame mixer una única vez

    game = BoggleGame(
        archivo_palabras=GAME_SETTINGS.WORD_FILE,
        logo_path=UI_SETTINGS.LOGO_PATH,
        game_settings=GAME_SETTINGS,
        ui_settings=UI_SETTINGS
    )
    game.run()
    pygame.mixer.quit() # Cierra Pygame mixer al finalizar

if __name__ == "__main__":
    main()
