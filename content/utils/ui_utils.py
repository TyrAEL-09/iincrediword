import os

TOCAR_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'recursos', 'tocar.mp3')

def play_click_sound():
    """
    Reproduce un sonido de clic usando pygame.
    Args: Ninguno.
    Returns: None.
    Uso: Para dar feedback sonoro en los menús al pulsar botones.
    """
    try:
        import pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        sound = pygame.mixer.Sound(TOCAR_PATH)
        sound.play()
    except Exception:
        pass
