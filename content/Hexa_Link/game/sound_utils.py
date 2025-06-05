import pygame
import os

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
TOCAR_PATH = os.path.join(BASE_PATH, "recursos", "tocar.mp3")
GOOD_PATH = os.path.join(BASE_PATH, "recursos", "good.mp3")
FAIL_PATH = os.path.join(BASE_PATH, "recursos", "fail.mp3")
HAIKUE_PATH = os.path.join(BASE_PATH, "recursos", "haikue.m4a")  # Cambiado a .m4a

def sonido_click():
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        sound = pygame.mixer.Sound(TOCAR_PATH)
        sound.play()
    except Exception:
        pass

def play_feedback_sound(success):
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        path = GOOD_PATH if success else FAIL_PATH
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            sound.play()
    except Exception:
        pass

def sonido_combo():
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        if os.path.exists(HAIKUE_PATH):
            sound = pygame.mixer.Sound(HAIKUE_PATH)
            sound.play()
    except Exception as e:
        print(f"[ERROR] No se pudo reproducir haikue.m4a: {e}")
