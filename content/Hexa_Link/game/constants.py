import os
import pygame
from pathlib import Path

# Screen configuration
WIDTH, HEIGHT = 800, 700
SIDEBAR_WIDTH = 200
GAME_AREA_WIDTH = WIDTH - SIDEBAR_WIDTH
FPS = 60

# Colors
BG_COLOR = (30, 30, 30)
HEX_COLOR = (50, 50, 50)
CENTER_COLOR = (0, 191, 255)  # Cambiado de amarillo a #00BFFF
TEXT_COLOR = (230, 230, 230)
FOUND_COLOR = (76, 175, 80)
BUTTON_COLOR = (70, 70, 70)
SIDEBAR_BG = (40, 40, 40)
ERROR_COLOR = (255, 100, 100)
HOVER_COLOR = (100, 100, 150)
PAUSE_OVERLAY = (0, 0, 0, 180)
PAUSE_BORDER = (255, 215, 0)

# Game settings
MIN_WORDS, MAX_WORDS = 50, 100
MIN_letras = 3
POINTS_PER_LETTER = 20
HEX_SIZE = 60
COMBO_MULTIPLIERS = {
    2: 1.25,
    5: 1.5,
    10: 2.0
}
COMBO_DURATION_MS = 2000

# Path configuration
BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"
WORDS_FILE = ASSETS_DIR / "palabraspremium_actualizado.txt"
ANIMATIONS_DIR = ASSETS_DIR / "animations"

# Fuente personalizada
FONT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "recursos", "Jersey20-Regular.ttf")
pygame.font.init()
try:
    FONT_LARGE = pygame.font.Font(FONT_PATH, 48)
    FONT_MEDIUM = pygame.font.Font(FONT_PATH, 24)
    FONT_SMALL = pygame.font.Font(FONT_PATH, 20)
except:
    FONT_LARGE = pygame.font.SysFont('Arial', 48)
    FONT_MEDIUM = pygame.font.SysFont('Arial', 24)
    FONT_SMALL = pygame.font.SysFont('Arial', 20)

# Cursores
ARROW_CURSOR = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
HAND_CURSOR = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)

# Geometria Hexagonal
HEX_RADIUS = HEX_SIZE * 3**0.5
HEX_ANGLES = [0, 60, 120, 180, 240, 300]

# Configuración de botones
BUTTON_WIDTH, BUTTON_HEIGHT = 120, 40
BUTTON_RADIUS = 4

PAUSE_OVERLAY = (0, 0, 0, 180)  # Negro semitransparente (R, G, B, Alpha)

# Ruta a la música principal
MUSIC_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "recursos", "Balatro Main Theme.mp3")
