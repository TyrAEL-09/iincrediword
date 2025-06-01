import pygame
import os
from .constants import *
from .game_state import GameState
from .ui_elements import *
from .animations import FireAnimation
from PIL import Image

MUSIC_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "recursos", "Balatro Main Theme.mp3")
NOMUSICA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "recursos", "nomusica.png")
TOCAR_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "recursos", "tocar.mp3")

def play_click_sound():
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        sound = pygame.mixer.Sound(TOCAR_PATH)
        sound.play()
    except Exception:
        pass

class HexGame:
    def __init__(self, usuario=None, game_state=None):
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

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        if not self.game_state.paused:
            over_btn = any(r.collidepoint(mouse_pos) for r in [
                self.game_state.btn_del_rect, 
                self.game_state.btn_clear_rect, 
                self.game_state.btn_shuffle_rect,  # Incluye el nuevo botón
                self.game_state.btn_check_rect, 
                self.game_state.btn_pause_rect
            ])
            
            over_hex = is_over_hexagon(
                mouse_pos[0], mouse_pos[1],
                self.game_state.positions,
                self.game_state.letters,
                HEX_SIZE
            )
            
            pygame.mouse.set_cursor(HAND_CURSOR if over_btn or over_hex else ARROW_CURSOR)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.KEYDOWN:
                    self.game_state.combo_msg = ""
                    # play_click_sound()  # Eliminado: ya no suena al escribir
                    if event.key == pygame.K_RETURN:
                        self.game_state.submit_word()
                    elif event.key == pygame.K_BACKSPACE:
                        self.game_state.delete_last_letter()
                    else:
                        ch = event.unicode.lower()
                        if ch in self.game_state.letters:
                            self.game_state.current_word += ch
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Botón pausa
                    if self.game_state.btn_pause_rect.collidepoint(mouse_pos):
                        play_click_sound()
                        self.game_state.toggle_pause()
                        # Pausar música al entrar en pausa
                        if self.game_state.paused and self.music_on:
                            pygame.mixer.music.pause()
                        elif not self.game_state.paused and self.music_on:
                            pygame.mixer.music.unpause()
                    
                    # Botón comprobar
                    elif self.game_state.btn_check_rect.collidepoint(mouse_pos):
                        play_click_sound()
                        self.game_state.submit_word()
                    # Botón borrar
                    elif self.game_state.btn_del_rect.collidepoint(mouse_pos):
                        play_click_sound()
                        self.game_state.delete_last_letter()
                    # Botón limpiar
                    elif self.game_state.btn_clear_rect.collidepoint(mouse_pos):
                        play_click_sound()
                        self.game_state.clear_word()
                    # Botón reordenar
                    elif self.game_state.btn_shuffle_rect.collidepoint(mouse_pos):
                        play_click_sound()
                        self.game_state.shuffle_letters()
                    # Botón música
                    elif self.music_btn_rect.collidepoint(mouse_pos):
                        play_click_sound()
                        self.music_on = not self.music_on
                        if self.music_on:
                            pygame.mixer.music.unpause()
                        else:
                            pygame.mixer.music.pause()
                    else:
                        for i, letter in enumerate(self.game_state.letters):
                            pts = hexagon_points(self.game_state.positions[i], HEX_SIZE)
                            surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                            pygame.draw.polygon(surf, (255, 255, 255), pts)
                            if pygame.mask.from_surface(surf).get_at(mouse_pos):
                                self.game_state.combo_msg = ""  # Limpiar mensaje de combo
                                self.game_state.current_word += letter
                                break
        else:
            pygame.mouse.set_cursor(HAND_CURSOR)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    resume_btn, save_btn, menu_btn = draw_pause_screen(self.screen, mouse_pos)
                    if resume_btn.collidepoint(mouse_pos):
                        play_click_sound()
                        self.game_state.toggle_pause()
                        # Reanudar música al salir de la pausa
                        if not self.game_state.paused and self.music_on:
                            pygame.mixer.music.unpause()
                    elif save_btn.collidepoint(mouse_pos):
                        play_click_sound()
                        self.guardar_partida()
                    elif menu_btn.collidepoint(mouse_pos):
                        play_click_sound()
                        if not self.partida_guardada:
                            self.mostrar_confirmacion_salida()
                        else:
                            self.running = False
                            pygame.quit()
                            from menus.seleccion_juego import iniciar_menu
                            iniciar_menu(self.usuario)

    def guardar_partida(self):
        if not self.usuario:
            return
        from Hexa_Link.run_game import save_game_state
        save_game_state(self.usuario, self.game_state)
        self.save_message = "¡Partida guardada exitosamente!"
        self.save_message_timer = pygame.time.get_ticks()
        self.partida_guardada = True
        print(f"Partida guardada para {self.usuario}")

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

    def mostrar_menu_victoria(self):
        scores = self.guardar_puntaje()
        running = True
        while running:
            self.screen.fill((30, 42, 56))  # Color #1e2a38
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill(PAUSE_OVERLAY)
            self.screen.blit(overlay, (0, 0))

            # Mensaje principal
            title = FONT_LARGE.render("¡Felicidades! Partida completada!", True, CENTER_COLOR)
            title_rect = title.get_rect(center=(WIDTH//2, 80))
            msg_bg = title_rect.inflate(40, 40)
            pygame.draw.rect(self.screen, (30, 42, 56), msg_bg, border_radius=10)
            pygame.draw.rect(self.screen, CENTER_COLOR, msg_bg, 2, border_radius=10)
            self.screen.blit(title, title_rect)

            # Puntuación
            score_txt = FONT_MEDIUM.render(f"Tu puntuación: {self.game_state.score}", True, TEXT_COLOR)
            score_rect = score_txt.get_rect(center=(WIDTH//2, 140))
            self.screen.blit(score_txt, score_rect)

            # Tablero de puntajes
            board_w, board_h = 500, 340
            board_rect = pygame.Rect(WIDTH//2 - board_w//2, 180, board_w, board_h)
            pygame.draw.rect(self.screen, CENTER_COLOR, board_rect, border_radius=16)
            pygame.draw.rect(self.screen, (255,255,255), board_rect, 2, border_radius=16)
            board_title = FONT_MEDIUM.render("Top 10 Puntajes", True, (255,255,255))
            self.screen.blit(board_title, board_title.get_rect(center=(WIDTH//2, 210)))
            y0 = 240
            for idx, entry in enumerate(scores):
                usuario = entry["usuario"]
                puntaje = entry["score"]
                color = (255,255,255) if idx != 0 else (255, 215, 0)  # Oro para el primero
                txt = FONT_MEDIUM.render(f"{idx+1}. {usuario} - {puntaje}", True, color)
                self.screen.blit(txt, (WIDTH//2 - board_w//2 + 30, y0 + idx*28))

            # Botón volver al menú (más largo y letras blancas)
            btn_width, btn_height = 420, 54
            btn_rect = pygame.Rect(WIDTH//2 - btn_width//2, 180+board_h+30, btn_width, btn_height)
            mouse_pos = pygame.mouse.get_pos()
            btn_color = CENTER_COLOR if btn_rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=BUTTON_RADIUS)
            pygame.draw.rect(self.screen, CENTER_COLOR, btn_rect, 2, border_radius=BUTTON_RADIUS)
            btn_label = FONT_MEDIUM.render("Volver al menú de selección de juegos", True, (255,255,255))
            self.screen.blit(btn_label, btn_label.get_rect(center=btn_rect.center))

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_rect.collidepoint(mouse_pos):
                        # Volver al menú de selección de juegos
                        pygame.quit()
                        from menus.seleccion_juego import iniciar_menu
                        iniciar_menu(self.usuario)
                        return

    def mostrar_confirmacion_salida(self):
        running = True
        while running:
            self.screen.fill((30, 42, 56))
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill(PAUSE_OVERLAY)
            self.screen.blit(overlay, (0, 0))
            # Mensaje
            title = FONT_LARGE.render("La partida actual no se ha guardado", True, CENTER_COLOR)
            title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 60))
            msg_bg = title_rect.inflate(40, 40)
            pygame.draw.rect(self.screen, (30, 42, 56), msg_bg, border_radius=10)
            pygame.draw.rect(self.screen, CENTER_COLOR, msg_bg, 2, border_radius=10)
            self.screen.blit(title, title_rect)
            msg2 = FONT_MEDIUM.render("¿Deseas salir de todos modos?", True, (255,255,255))
            self.screen.blit(msg2, msg2.get_rect(center=(WIDTH//2, HEIGHT//2 - 10)))
            # Botones
            btn_w, btn_h = 220, 48
            btn1 = pygame.Rect(WIDTH//2 - btn_w - 20, HEIGHT//2 + 40, btn_w, btn_h)
            btn2 = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 40, btn_w, btn_h)
            mouse_pos = pygame.mouse.get_pos()
            color1 = CENTER_COLOR if btn1.collidepoint(mouse_pos) else BUTTON_COLOR
            color2 = CENTER_COLOR if btn2.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(self.screen, color1, btn1, border_radius=BUTTON_RADIUS)
            pygame.draw.rect(self.screen, CENTER_COLOR, btn1, 2, border_radius=BUTTON_RADIUS)
            pygame.draw.rect(self.screen, color2, btn2, border_radius=BUTTON_RADIUS)
            pygame.draw.rect(self.screen, CENTER_COLOR, btn2, 2, border_radius=BUTTON_RADIUS)
            label1 = FONT_MEDIUM.render("Salir y guardar", True, (255,255,255))
            label2 = FONT_MEDIUM.render("Salir y no guardar", True, (255,255,255))
            self.screen.blit(label1, label1.get_rect(center=btn1.center))
            self.screen.blit(label2, label2.get_rect(center=btn2.center))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn1.collidepoint(mouse_pos):
                        self.guardar_partida()
                        self.running = False
                        pygame.quit()
                        from menus.seleccion_juego import iniciar_menu
                        iniciar_menu(self.usuario)
                        return
                    elif btn2.collidepoint(mouse_pos):
                        self.running = False
                        pygame.quit()
                        from menus.seleccion_juego import iniciar_menu
                        iniciar_menu(self.usuario)
                        return

    def draw(self):
        self.screen.fill(BG_COLOR)
        
        if not self.game_state.paused:
            # Dibujar juego normal
            draw_word_count(self.screen, len(self.game_state.found_words), self.game_state.target_count)
            draw_hexagons(self.screen, self.game_state.positions, self.game_state.letters, 
                         self.game_state.center_letter, pygame.mouse.get_pos())
            draw_current_word(self.screen, self.game_state.current_word)
            draw_game_buttons(self.screen, self.game_state, pygame.mouse.get_pos())
            draw_score(self.screen, self.game_state.score)
            draw_combo_message(self.screen, self.game_state.combo_msg, self.game_state.combo_timer)
            draw_sidebar(self.screen, self.game_state.valid_by_initial, self.game_state.found_words)
            draw_time(self.screen, self.game_state.get_elapsed_time())
            self.fire_animation.draw(self.screen, self.game_state.combo_count)
            
            if self.game_state.is_game_complete():
                if self.music_on:
                    pygame.mixer.music.stop()
                self.mostrar_menu_victoria()
                return
            
            # Botón música
            color = CENTER_COLOR if self.music_on else (200, 0, 0)
            pygame.draw.rect(self.screen, color, self.music_btn_rect, border_radius=8)
            if self.music_on:
                icon = "♪"
                font = pygame.font.SysFont('Arial', 32)
                text = font.render(icon, True, (255,255,255))
                text_rect = text.get_rect(center=self.music_btn_rect.center)
                self.screen.blit(text, text_rect)
            else:
                if self.nomusica_img:
                    img_rect = self.nomusica_img.get_rect(center=self.music_btn_rect.center)
                    self.screen.blit(self.nomusica_img, img_rect)
                else:
                    font = pygame.font.SysFont('Arial', 32)
                    text = font.render("✕", True, (255,255,255))
                    text_rect = text.get_rect(center=self.music_btn_rect.center)
                    self.screen.blit(text, text_rect)
            
            if self.save_message and pygame.time.get_ticks() - self.save_message_timer < 1800:
                font = pygame.font.SysFont('Arial', 22, bold=True)
                text = font.render(self.save_message, True, (0,191,255))
                rect = text.get_rect(center=(WIDTH//2, HEIGHT-40))
                pygame.draw.rect(self.screen, (30,30,30), rect.inflate(30,16), border_radius=8)
                self.screen.blit(text, rect)
            elif self.save_message:
                self.save_message = None
        else:
            # Dibujar pantalla de pausa
            draw_pause_screen(self.screen, pygame.mouse.get_pos())
            if self.save_message and pygame.time.get_ticks() - self.save_message_timer < 1800:
                font = pygame.font.SysFont('Arial', 22, bold=True)
                text = font.render(self.save_message, True, (0,191,255))
                rect = text.get_rect(center=(WIDTH//2, HEIGHT-40))
                pygame.draw.rect(self.screen, (30,30,30), rect.inflate(30,16), border_radius=8)
                self.screen.blit(text, rect)
            elif self.save_message:
                self.save_message = None
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            if not self.running:
                break
            self.fire_animation.update(self.game_state.combo_count)
            self.draw()
        pygame.quit()
        os._exit(0)  # Forzar cierre total del proceso y la terminal