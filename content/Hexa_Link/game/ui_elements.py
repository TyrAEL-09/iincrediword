# Este archivo contiene funciones de dibujo y utilidades para la interfaz gráfica del juego Hexa-Link.
# Incluye funciones para dibujar hexágonos, botones, barra lateral, mensajes y otros elementos visuales.

import pygame
import math
import os
from Hexa_Link.game.constants import *
from PIL import Image

# Calcula los puntos de un hexágono dados su centro y tamaño.
def hexagon_points(center, size):
    cx, cy = center
    return [(cx + size * math.cos(math.radians(60*i - 30)), cy + size * math.sin(math.radians(60*i - 30))) for i in range(6)]

# Detecta si el mouse está sobre algún hexágono.
def is_over_hexagon(mx, my, positions, letters, hex_size):
    # Evita errores si el mouse está fuera de la pantalla
    if not (0 <= mx < WIDTH and 0 <= my < HEIGHT):
        return False
    for i in range(len(letters)):
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pts = hexagon_points(positions[i], hex_size)
        pygame.draw.polygon(surf, (255, 255, 255), pts)
        mask = pygame.mask.from_surface(surf)
        if mask.get_at((mx, my)):
            return True
    return False

# Dibuja todos los hexágonos del tablero, resaltando el central y el que está bajo el mouse.
def draw_hexagons(screen, positions, letters, center_letter, mouse_pos):
    for i, letter in enumerate(letters):
        pts = hexagon_points(positions[i], HEX_SIZE)
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (255, 255, 255), pts)
        # Evita errores si el mouse está fuera de la pantalla
        hover = False
        if 0 <= mouse_pos[0] < WIDTH and 0 <= mouse_pos[1] < HEIGHT:
            hover = pygame.mask.from_surface(surf).get_at(mouse_pos)
        hex_color = HOVER_COLOR if hover else (CENTER_COLOR if letter == center_letter else HEX_COLOR)
        pygame.draw.polygon(screen, hex_color, pts)
        
        text_color = (0, 0, 0) if letter == center_letter else TEXT_COLOR
        txt = FONT_LARGE.render(letter.upper(), True, text_color)
        screen.blit(txt, txt.get_rect(center=positions[i]))

# Carga una imagen y la convierte a pygame.Surface, útil para iconos de botones.
def load_ctk_image(path, size):
    # Utilidad para cargar imagen y convertir a pygame.Surface
    img = Image.open(path).convert("RGBA").resize(size, Image.LANCZOS)
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode)

# Carga las imágenes de iconos solo una vez para eficiencia.
RECURSOS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "recursos")
PAUSA_IMG = load_ctk_image(os.path.join(RECURSOS_DIR, "pausa.png"), (40, 40))
REORDENAR_IMG = load_ctk_image(os.path.join(RECURSOS_DIR, "reordenar.png"), (32, 32))

# Dibuja una lista de botones con su estado de hover y opcionalmente un icono.
def draw_buttons(screen, buttons, mouse_pos):
    for rect, label_text, icon in buttons:
        is_hover = rect.collidepoint(mouse_pos)
        btn_color = HOVER_COLOR if is_hover else CENTER_COLOR
        pygame.draw.rect(screen, btn_color, rect, border_radius=BUTTON_RADIUS)
        pygame.draw.rect(screen, CENTER_COLOR, rect, 2, border_radius=BUTTON_RADIUS)
        if icon:
            icon_rect = icon.get_rect(center=rect.center)
            screen.blit(icon, icon_rect)
        else:
            label = FONT_MEDIUM.render(label_text, True, (0, 0, 0))
            screen.blit(label, label.get_rect(center=rect.center))

# Dibuja los botones principales del juego (comprobar, borrar, reordenar, eliminar, pausa).
def draw_game_buttons(screen, game_state, mouse_pos):
    # Distribución según la imagen proporcionada
    # Comprobar (arriba, centrado)
    comprobar_rect = game_state.btn_check_rect
    # Fila inferior: Borrar, Reordenar (icono), Eliminar
    borrar_rect = game_state.btn_del_rect
    reordenar_rect = game_state.btn_shuffle_rect
    eliminar_rect = game_state.btn_clear_rect
    # Botón de pausa (arriba derecha)
    pausa_rect = game_state.btn_pause_rect

    # Dibuja los botones principales
    draw_buttons(screen, [
        (comprobar_rect, "Comprobar", None),
        (borrar_rect, "Borrar", None),
        (reordenar_rect, "", REORDENAR_IMG),
        (eliminar_rect, "Eliminar", None),
    ], mouse_pos)

    # Botón de pausa con icono
    btn_color = CENTER_COLOR  # Azul del centro para el botón de pausa
    pygame.draw.rect(screen, btn_color, pausa_rect, border_radius=BUTTON_RADIUS)
    pygame.draw.rect(screen, CENTER_COLOR, pausa_rect, 2, border_radius=BUTTON_RADIUS)
    icon_rect = PAUSA_IMG.get_rect(center=pausa_rect.center)
    screen.blit(PAUSA_IMG, icon_rect)

# Dibuja la sección especial de la barra lateral para el heptacrack.
def draw_heptacrack_sidebar(screen, heptacrack, found_words):
    sidebar_x = WIDTH - SIDEBAR_WIDTH
    y = 20
    fh = FONT_SMALL.get_height()
    # Fondo del título
    pygame.draw.rect(screen, (40, 60, 40), (sidebar_x+5, y, SIDEBAR_WIDTH-10, fh+18), border_radius=8)
    # Título en azul central
    label = FONT_SMALL.render("HEPTACRACK", True, CENTER_COLOR)
    screen.blit(label, (sidebar_x+20, y+4))
    y += fh+18
    # Si fue encontrada, muestra la palabra en grande y verde
    if heptacrack and heptacrack in found_words:
        word = FONT_MEDIUM.render(heptacrack.upper(), True, FOUND_COLOR)
        screen.blit(word, (sidebar_x+20, y))
        y += word.get_height() + 10
    return y

# Dibuja la barra lateral con las palabras encontradas, agrupadas por inicial.
def draw_sidebar(screen, valid_by_initial, found_words, heptacrack=None):
    # Crea el fondo de la barra lateral
    sidebar = pygame.Rect(WIDTH-SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT)
    pygame.draw.rect(screen, SIDEBAR_BG, sidebar)
    # Variables de control de layout
    y, max_height, fh, maxw = 20, HEIGHT-40, FONT_SMALL.get_height(), SIDEBAR_WIDTH-30
    # Dibuja primero la sección especial del heptacrack si existe
    if heptacrack:
        y = draw_heptacrack_sidebar(screen, heptacrack, found_words)
        y += 10
    # Recorre las palabras agrupadas por inicial
    for ini, lst in sorted(valid_by_initial.items()):
        # Cuenta cuántas palabras encontradas empiezan con esta inicial
        cnt = sum(w.startswith(ini) for w in found_words)
        # Lista de palabras encontradas (en mayúsculas), excluyendo la heptacrack
        found = [w.upper() for w in found_words if w.startswith(ini) and w != heptacrack]
        # Si no hay espacio suficiente, termina el dibujo
        if y + fh > max_height: break
        # Dibuja el encabezado de la sección (ej: (2/5) con A)
        screen.blit(FONT_SMALL.render(f"({cnt}/{len(lst)}) con {ini.upper()}", True, TEXT_COLOR), (WIDTH-SIDEBAR_WIDTH+10, y))
        y += fh
        # Si hay palabras encontradas, las muestra en líneas, separadas por coma
        if found:
            line, lines = "", 0
            for word in found:
                # Intenta agregar la palabra a la línea actual
                test = (line + ", " if line else "") + word
                # Si la línea se pasa del ancho máximo, la dibuja y comienza una nueva
                if FONT_SMALL.size(test)[0] > maxw:
                    if line:
                        # Dibuja la línea de palabras halladas sobre un fondo negro semitransparente para máxima visibilidad
                        word_rect = pygame.Rect(WIDTH-SIDEBAR_WIDTH+20, y, FONT_SMALL.size(line)[0], fh)
                        overlay = pygame.Surface((word_rect.width, word_rect.height), pygame.SRCALPHA)
                        overlay.fill((0,0,0,180))
                        screen.blit(overlay, word_rect.topleft)
                        screen.blit(FONT_SMALL.render(line, True, FOUND_COLOR), (WIDTH-SIDEBAR_WIDTH+20, y))
                        y += fh
                        if y + fh > max_height: break
                    line = word
                    lines += 1
                else:
                    line = test
            # Dibuja la última línea si queda espacio
            if line and y + fh <= max_height:
                word_rect = pygame.Rect(WIDTH-SIDEBAR_WIDTH+20, y, FONT_SMALL.size(line)[0], fh)
                overlay = pygame.Surface((word_rect.width, word_rect.height), pygame.SRCALPHA)
                overlay.fill((0,0,0,180))
                screen.blit(overlay, word_rect.topleft)
                screen.blit(FONT_SMALL.render(line, True, FOUND_COLOR), (WIDTH-SIDEBAR_WIDTH+20, y))
                y += fh
        # Espacio extra entre secciones
        y += 5

# Dibuja la pantalla de pausa con botones de reanudar, guardar y volver al menú principal.
def draw_pause_screen(screen, mouse_pos):
    # Fondo semitransparente
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(PAUSE_OVERLAY)
    screen.blit(overlay, (0, 0))
    
    # Mensaje principal
    pause_text = FONT_LARGE.render("JUEGO EN PAUSA", True, CENTER_COLOR)
    text_rect = pause_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 110))
    
    # Fondo del mensaje
    msg_background = text_rect.inflate(40, 40)
    pygame.draw.rect(screen, BG_COLOR, msg_background, border_radius=10)
    pygame.draw.rect(screen, CENTER_COLOR, msg_background, 2, border_radius=10)
    screen.blit(pause_text, text_rect)
    
    BUTTON_WIDTH = 320  # Aumentar el ancho de los botones
    BUTTON_HEIGHT = 50

    # Botón de reanudar
    resume_btn = pygame.Rect(WIDTH//2 - BUTTON_WIDTH//2, HEIGHT//2 - 30, BUTTON_WIDTH, BUTTON_HEIGHT)
    btn_color = HOVER_COLOR if resume_btn.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, btn_color, resume_btn, border_radius=BUTTON_RADIUS)
    pygame.draw.rect(screen, CENTER_COLOR, resume_btn, 2, border_radius=BUTTON_RADIUS)
    resume_text = FONT_MEDIUM.render("REANUDAR", True, TEXT_COLOR)
    screen.blit(resume_text, resume_text.get_rect(center=resume_btn.center))

    # Botón de guardar partida
    save_btn = pygame.Rect(WIDTH//2 - BUTTON_WIDTH//2, HEIGHT//2 + 30, BUTTON_WIDTH, BUTTON_HEIGHT)
    save_color = HOVER_COLOR if save_btn.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, save_color, save_btn, border_radius=BUTTON_RADIUS)
    pygame.draw.rect(screen, CENTER_COLOR, save_btn, 2, border_radius=BUTTON_RADIUS)
    save_text = FONT_MEDIUM.render("GUARDAR PARTIDA", True, TEXT_COLOR)
    screen.blit(save_text, save_text.get_rect(center=save_btn.center))

    # Botón volver al menú principal
    menu_btn = pygame.Rect(WIDTH//2 - BUTTON_WIDTH//2, HEIGHT//2 + 90, BUTTON_WIDTH, BUTTON_HEIGHT)
    menu_color = HOVER_COLOR if menu_btn.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, menu_color, menu_btn, border_radius=BUTTON_RADIUS)
    pygame.draw.rect(screen, CENTER_COLOR, menu_btn, 2, border_radius=BUTTON_RADIUS)
    menu_text = FONT_MEDIUM.render("VOLVER AL MENÚ PRINCIPAL", True, TEXT_COLOR)
    screen.blit(menu_text, menu_text.get_rect(center=menu_btn.center))

    return resume_btn, save_btn, menu_btn

# Dibuja la palabra que el usuario está formando actualmente.
def draw_current_word(screen, current_word):
    curr_txt = FONT_MEDIUM.render(current_word.upper(), True, TEXT_COLOR)
    screen.blit(curr_txt, (GAME_AREA_WIDTH // 2 - curr_txt.get_width() // 2, HEIGHT - 280))

# Dibuja el puntaje actual del jugador.
def draw_score(screen, score):
    score_txt = FONT_MEDIUM.render(f"Puntos: {score}", True, TEXT_COLOR)
    screen.blit(score_txt, (GAME_AREA_WIDTH // 2 - score_txt.get_width() // 2, HEIGHT - 85))

# Dibuja el mensaje de combo si está activo.
def draw_combo_message(screen, combo_msg, combo_timer):
    if combo_msg and pygame.time.get_ticks() - combo_timer < COMBO_DURATION_MS:
        msg = FONT_MEDIUM.render(combo_msg, True, FOUND_COLOR)
        screen.blit(msg, (GAME_AREA_WIDTH // 2 - msg.get_width() // 2, HEIGHT - 280))

# Dibuja el tiempo transcurrido de la partida.
def draw_time(screen, elapsed_time):
    m, s = divmod(elapsed_time, 60)
    time_txt = FONT_MEDIUM.render(f"Tiempo: {m:02}:{s:02}", True, TEXT_COLOR)
    screen.blit(time_txt, (20, 20))

# Dibuja el contador de palabras halladas vs objetivo.
def draw_word_count(screen, found_count, target_count):
    found_txt = FONT_MEDIUM.render(f"Palabras halladas: ({found_count}/{target_count})", True, TEXT_COLOR)
    screen.blit(found_txt, (GAME_AREA_WIDTH // 2 - found_txt.get_width() // 2, HEIGHT // 3 - HEX_RADIUS - 85))

# Dibuja el mensaje de victoria cuando el jugador gana.
def draw_victory_message(screen):
    w = FONT_LARGE.render("¡Has ganado!", True, FOUND_COLOR)
    screen.blit(w, (GAME_AREA_WIDTH // 2 - w.get_width() // 2, HEIGHT // 2))

# Dibuja el mensaje de feedback (bien/mal) tras comprobar una palabra.
def draw_word_feedback(screen, game_state):
    # Muestra el mensaje de acierto o error reciente
    # Si existe un feedback reciente, lo muestra en pantalla
    if hasattr(game_state, 'last_word_feedback') and game_state.last_word_feedback:
        msg, is_ok, ts = game_state.last_word_feedback
        color = FOUND_COLOR if is_ok else (255, 60, 60)
        # Solo mostrar si no han pasado más de 1200 ms
        if pygame.time.get_ticks() - ts < 1200:
            font = FONT_MEDIUM
            # Renderiza el texto del mensaje
            text = font.render(msg, True, color)
            # 20 píxeles más abajo respecto a antes (antes era -310, ahora -300)
            rect = text.get_rect(center=(GAME_AREA_WIDTH // 2, HEIGHT - 295))
            # Dibuja un fondo oscuro detrás del mensaje
            pygame.draw.rect(screen, (30,30,30), rect.inflate(30,16), border_radius=8)
            # Dibuja el mensaje en pantalla
            screen.blit(text, rect)