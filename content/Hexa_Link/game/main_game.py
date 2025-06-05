# Archivo principal de la lógica y ciclo de juego de Hexa-Link.

# === IMPORTACIONES ===
import pygame
import os
from .constants import *
from .game_state import GameState
from .ui_elements import *
from .animations import FireAnimation
from PIL import Image
from .sound_utils import sonido_click, play_feedback_sound, sonido_combo
from .special_screens import menu_victoria, mostrar_confirmacion_salida
from .event_handler import handle_events
from .draw_game import draw_game


# === RUTAS A RECURSOS ===
MUSIC_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "recursos", "Balatro Main Theme.mp3")
NOMUSICA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "recursos", "nomusica.png")


# === CLASE PRINCIPAL DEL JUEGO ===
class HexGame:
    def __init__(self, usuario=None, game_state=None):
        """
        Inicializa la ventana, estado, música y recursos del juego.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Juego de Hexágonos")
        self.clock = pygame.time.Clock()
        self.usuario = usuario

        # Estado del juego
        if game_state is not None:
            self.game_state = game_state
        else:
            self.game_state = GameState()

        # Animación de fuego
        self.fire_animation = FireAnimation()
        self.running = True

        # Música
        self.music_on = True
        pygame.mixer.init()
        if os.path.exists(MUSIC_PATH):
            pygame.mixer.music.load(MUSIC_PATH)
            pygame.mixer.music.play(-1)

        # Botón música
        self.music_boton_rect = pygame.Rect(20, HEIGHT - 70, 50, 50)

        # Cargar icono nomusica
        self.nomusica_img = None
        if os.path.exists(NOMUSICA_PATH):
            img = Image.open(NOMUSICA_PATH).convert("RGBA").resize((25, 35), Image.LANCZOS)
            self.nomusica_img = pygame.image.fromstring(img.tobytes(), img.size, img.mode)

        # Mensaje de guardado
        self.save_message = None
        self.save_message_timer = 0

        # Si game_state viene de cargar partida, la consideramos guardada
        self.partida_guardada = game_state is not None


    # === GUARDADO DE PARTIDA ===
    def guardar_partida(self):
        """
        Guarda el estado actual de la partida en disco.
        """
        if not self.usuario:
            return
        from Hexa_Link.run_game import save_game_state
        save_game_state(self.usuario, self.game_state)
        self.save_message = "¡Partida guardada exitosamente!"
        self.save_message_timer = pygame.time.get_ticks()
        self.partida_guardada = True
        print(f"Partida guardada para {self.usuario}")


    # === GUARDADO DE PUNTAJE ===
    def guardar_puntaje(self):
        """
        Guarda el puntaje final en el top 10 de puntajes.
        """
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


    # === CICLO PRINCIPAL DEL JUEGO ===
    def run(self):
        """
        Bucle principal: maneja eventos, animaciones y renderizado.
        """
        while self.running:
            self.clock.tick(FPS)
            handle_events(self)
            if not self.running:
                break
            self.fire_animation.update(self.game_state.combo_cont)
            draw_game(self)
        pygame.quit()
        os._exit(0)  # Forzar cierre total del proceso y la terminal