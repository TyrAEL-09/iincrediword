# Archivo principal de la lógica y ciclo de juego de Hexa-Link.

import pygame
import os
from .constants import *
from .game_state import GameState
from .ui_elements import *
from .animations import FireAnimation
from PIL import Image
from .sound_utils import play_click_sound, play_feedback_sound, play_combo_sound
from .special_screens import mostrar_menu_victoria, mostrar_confirmacion_salida
from .event_handler import handle_events
from .draw_game import draw_game

# Rutas a recursos de música e imágenes
MUSIC_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "recursos", "Balatro Main Theme.mp3")
NOMUSICA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "recursos", "nomusica.png")

# Clase principal del juego Hexa-Link
class HexGame:
    def __init__(self, usuario=None, game_state=None):
        # Inicializa la ventana, estado, música y recursos
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Juego de Hexágonos")
        self.clock = pygame.time.Clock()
        self.usuario = usuario
        if game_state is not None:
            self.game_state = game_state
        else:
            self.game_state = GameState()
        self.fire_animation = FireAnimation()
        self.running = True
        # Música
        self.music_on = True
        pygame.mixer.init()
        if os.path.exists(MUSIC_PATH):
            pygame.mixer.music.load(MUSIC_PATH)
            pygame.mixer.music.play(-1)
        # Botón música
        self.music_btn_rect = pygame.Rect(20, HEIGHT - 70, 50, 50)
        # Cargar icono nomusica
        self.nomusica_img = None
        if os.path.exists(NOMUSICA_PATH):
            img = Image.open(NOMUSICA_PATH).convert("RGBA").resize((25, 35), Image.LANCZOS)
            self.nomusica_img = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
        self.save_message = None
        self.save_message_timer = 0
        # Si game_state viene de cargar partida, la consideramos guardada
        self.partida_guardada = game_state is not None

    # Guarda el estado actual de la partida
    def guardar_partida(self):
        if not self.usuario:
            return
        from Hexa_Link.run_game import save_game_state
        save_game_state(self.usuario, self.game_state)
        self.save_message = "¡Partida guardada exitosamente!"
        self.save_message_timer = pygame.time.get_ticks()
        self.partida_guardada = True
        print(f"Partida guardada para {self.usuario}")

    # Guarda el puntaje final en el top 10
    def guardar_puntaje(self):
        import json
        scores_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scores.json")
        usuario = self.usuario if self.usuario else "anonimo"
        try:
            if os.path.exists(scores_path):
                with open(scores_path, "r", encoding="utf-8") as f:
                    scores = json.load(f)
            else:
                scores = []
        except Exception:
            scores = []
        scores.append({"usuario": usuario, "score": self.game_state.score})
        scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
        with open(scores_path, "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
        return scores

    # Ciclo principal del juego: eventos, animaciones y renderizado
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            handle_events(self)
            if not self.running:
                break
            self.fire_animation.update(self.game_state.combo_count)
            draw_game(self)
        pygame.quit()
        os._exit(0)  # Forzar cierre total del proceso y la terminal