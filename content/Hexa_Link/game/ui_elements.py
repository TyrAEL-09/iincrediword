# Este archivo contiene funciones de dibujo y utilidades para la interfaz gráfica del juego Hexa-Link.
# Incluye funciones para dibujar hexágonos, botones, barra lateral, mensajes y otros elementos visuales.

# === IMPORTACIONES ===
import pygame
import math
import os
from Hexa_Link.game.constants import *
from PIL import Image


# === FUNCIONES DE GEOMETRÍA Y COLISIÓN ===
def hexagon_points(center, size):
    """Calcula los puntos de un hexágono dados su centro y tamaño."""
    cx, cy = center
    return [(cx + size * math.cos(math.radians(60*i - 30)), cy + size * math.sin(math.radians(60*i - 30))) for i in range(6)]


def is_over_hexagon(mx, my, posiciones, letras, hex_size):
    """Detecta si el mouse está sobre algún hexágono."""
    if not (0 <= mx < WIDTH and 0 <= my < HEIGHT):
        return False
    for i in range(len(letras)):
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pts = hexagon_points(posiciones[i], hex_size)
        pygame.draw.polygon(surf, (255, 255, 255), pts)
        mask = pygame.mask.from_surface(surf)
        if mask.get_at((mx, my)):
            return True
    return False


def point_in_hexagon(point, hex_points):
    """Algoritmo de cruce de rayos para saber si un punto está dentro de un polígono (hexágono)."""
    x, y = point
    n = len(hex_points)
    inside = False
    p1x, p1y = hex_points[0]
    for i in range(n+1):
        p2x, p2y = hex_points[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


# === DIBUJO DE HEXÁGONOS Y BOTONES ===
def draw_hexagons(screen, posiciones, letras, letra_central, mouse_pos):
    """Dibuja todos los hexágonos del tablero, resaltando el central y el que está bajo el mouse."""
    for i, letter in enumerate(letras):
        pts = hexagon_points(posiciones[i], HEX_SIZE)
        hover = point_in_hexagon(mouse_pos, pts)
        hex_color = HOVER_COLOR if hover else (CENTER_COLOR if letter == letra_central else HEX_COLOR)
        pygame.draw.polygon(screen, hex_color, pts)
        text_color = (0, 0, 0) if letter == letra_central else TEXT_COLOR
        txt = FONT_LARGE.render(letter.upper(), True, text_color)
        screen.blit(txt, txt.get_rect(center=posiciones[i]))


def load_ctk_image(path, size):
    """Carga una imagen y la convierte a pygame.Surface, útil para iconos de botones."""
    img = Image.open(path).convert("RGBA").resize(size, Image.LANCZOS)
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode)


# === ICONOS Y RECURSOS ===
RECURSOS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "recursos")
PAUSA_IMG = load_ctk_image(os.path.join(RECURSOS_DIR, "pausa.png"), (40, 40))
REORDENAR_IMG = load_ctk_image(os.path.join(RECURSOS_DIR, "reordenar.png"), (32, 32))


def draw_buttons(screen, buttons, mouse_pos):
    """Dibuja una lista de botones con su estado de hover y opcionalmente un icono."""
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


def draw_game_buttons(screen, game_state, mouse_pos):
    """Dibuja los botones principales del juego (comprobar, borrar, reordenar, eliminar, pausa)."""
    comprobar_rect = game_state.btn_check_rect
    borrar_rect = game_state.btn_del_rect
    reordenar_rect = game_state.btn_shuffle_rect
    eliminar_rect = game_state.btn_clear_rect
    pausa_rect = game_state.btn_pause_rect
    draw_buttons(screen, [
        (comprobar_rect, "Comprobar", None),
        (borrar_rect, "Borrar", None),
        (reordenar_rect, "", REORDENAR_IMG),
        (eliminar_rect, "Eliminar", None),
    ], mouse_pos)
    btn_color = CENTER_COLOR
    pygame.draw.rect(screen, btn_color, pausa_rect, border_radius=BUTTON_RADIUS)
    pygame.draw.rect(screen, CENTER_COLOR, pausa_rect, 2, border_radius=BUTTON_RADIUS)
    icon_rect = PAUSA_IMG.get_rect(center=pausa_rect.center)
    screen.blit(PAUSA_IMG, icon_rect)


# === SIDEBAR Y PALABRAS HALLADAS ===
def draw_heptacrack_sidebar(screen, heptacrack, pal_encontradas):
    """Dibuja la sección especial de la barra lateral para el heptacrack."""
    sidebar_x = WIDTH - SIDEBAR_WIDTH
    y = 20
    fh = FONT_SMALL.get_height()
    pygame.draw.rect(screen, (40, 60, 40), (sidebar_x+5, y, SIDEBAR_WIDTH-10, fh+18), border_radius=8)
    label = FONT_SMALL.render("HEPTACRACK", True, CENTER_COLOR)
    screen.blit(label, (sidebar_x+20, y+4))
    y += fh+18
    if heptacrack and heptacrack in pal_encontradas:
        word = FONT_MEDIUM.render(heptacrack.upper(), True, FOUND_COLOR)
        screen.blit(word, (sidebar_x+20, y))
        y += word.get_height() + 10
    return y


def draw_sidebar(screen, por_inicial, pal_encontradas, heptacrack=None, scroll_offset=0):
    """Dibuja la barra lateral con las palabras encontradas, agrupadas por inicial, en una mini-ventana scrolleable."""
    sidebar_x = WIDTH - SIDEBAR_WIDTH
    sidebar_y = 0
    sidebar_h = HEIGHT
    pygame.draw.rect(screen, SIDEBAR_BG, (sidebar_x, sidebar_y, SIDEBAR_WIDTH, sidebar_h))
    y = 20
    if heptacrack:
        y = draw_heptacrack_sidebar(screen, heptacrack, pal_encontradas)
        y += 10
    window_x = sidebar_x + 8
    window_y = y
    window_w = SIDEBAR_WIDTH - 24
    window_h = 260
    pygame.draw.rect(screen, (30, 30, 30), (window_x-2, window_y-2, window_w+4, window_h+4), border_radius=10)
    pygame.draw.rect(screen, (60, 60, 60), (window_x, window_y, window_w, window_h), border_radius=8)
    if not hasattr(draw_sidebar, '_words_cache'):
        draw_sidebar._words_cache = {'key': None, 'surface': None, 'content_h': 0}
    cache_key = (tuple(sorted((k, tuple(sorted(v))) for k, v in por_inicial.items())), tuple(sorted(pal_encontradas)), heptacrack)
    if draw_sidebar._words_cache['key'] != cache_key:
        font = FONT_SMALL
        fh = font.get_height()
        words_surface = pygame.Surface((window_w, 1000), pygame.SRCALPHA)
        words_surface.fill((60, 60, 60))
        y2 = 8
        for ini, lst in sorted(por_inicial.items()):
            cnt = sum(w.startswith(ini) for w in pal_encontradas)
            words = [w.upper() for w in pal_encontradas if w.startswith(ini) and w != heptacrack]
            label = font.render(f"({cnt}/{len(lst)}) con {ini.upper()}", True, TEXT_COLOR)
            words_surface.blit(label, (8, y2))
            y2 += fh
            for word in words:
                word_label = font.render(word, True, FOUND_COLOR)
                words_surface.blit(word_label, (20, y2))
                y2 += fh + 2
            y2 += 8
        words_content_h = y2 + 8
        draw_sidebar._words_cache = {'key': cache_key, 'surface': words_surface, 'content_h': words_content_h}
    else:
        words_surface = draw_sidebar._words_cache['surface']
        words_content_h = draw_sidebar._words_cache['content_h']
    words_surface_visible = words_surface.subsurface((0, scroll_offset, window_w, min(window_h, max(0, words_content_h - scroll_offset))))
    screen.blit(words_surface_visible, (window_x, window_y))
    if words_content_h > window_h:
        bar_h = max(40, window_h * window_h // words_content_h)
        bar_y = window_y + (scroll_offset * (window_h - bar_h)) // (words_content_h - window_h)
        pygame.draw.rect(screen, (80, 80, 120), (window_x + window_w - 10, bar_y, 8, bar_h), border_radius=4)
    return window_y, window_h, words_content_h


# === PANTALLA DE PAUSA ===
def draw_pause_screen(screen, mouse_pos):
    """Dibuja la pantalla de pausa con botones de unpause, guardar y volver al menú principal."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(PAUSE_OVERLAY)
    screen.blit(overlay, (0, 0))
    # Dibuja el borde de la pausa
    pause_text = FONT_LARGE.render("JUEGO EN PAUSA", True, CENTER_COLOR)
    text_rect = pause_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 110))
    msg_background = text_rect.inflate(40, 40)
    pygame.draw.rect(screen, BG_COLOR, msg_background, border_radius=10)
    pygame.draw.rect(screen, CENTER_COLOR, msg_background, 2, border_radius=10)
    screen.blit(pause_text, text_rect)
    BUTTON_WIDTH = 320
    BUTTON_HEIGHT = 50

    resume_btn = pygame.Rect(WIDTH//2 - BUTTON_WIDTH//2, HEIGHT//2 - 30, BUTTON_WIDTH, BUTTON_HEIGHT)
    btn_color = HOVER_COLOR if resume_btn.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, btn_color, resume_btn, border_radius=BUTTON_RADIUS)
    pygame.draw.rect(screen, CENTER_COLOR, resume_btn, 2, border_radius=BUTTON_RADIUS)

    # Dibuja el texto del botón de reanudar
    resume_text = FONT_MEDIUM.render("REANUDAR", True, TEXT_COLOR)
    screen.blit(resume_text, resume_text.get_rect(center=resume_btn.center))
    save_btn = pygame.Rect(WIDTH//2 - BUTTON_WIDTH//2, HEIGHT//2 + 30, BUTTON_WIDTH, BUTTON_HEIGHT)
    save_color = HOVER_COLOR if save_btn.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, save_color, save_btn, border_radius=BUTTON_RADIUS)
    pygame.draw.rect(screen, CENTER_COLOR, save_btn, 2, border_radius=BUTTON_RADIUS)

    # Dibuja el texto del botón de guardar
    save_text = FONT_MEDIUM.render("GUARDAR PARTIDA", True, TEXT_COLOR)
    screen.blit(save_text, save_text.get_rect(center=save_btn.center))
    menu_btn = pygame.Rect(WIDTH//2 - BUTTON_WIDTH//2, HEIGHT//2 + 90, BUTTON_WIDTH, BUTTON_HEIGHT)
    menu_color = HOVER_COLOR if menu_btn.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, menu_color, menu_btn, border_radius=BUTTON_RADIUS)
    pygame.draw.rect(screen, CENTER_COLOR, menu_btn, 2, border_radius=BUTTON_RADIUS)
    # Dibuja el texto del botón de volver al menú

    menu_text = FONT_MEDIUM.render("VOLVER AL MENÚ PRINCIPAL", True, TEXT_COLOR)
    screen.blit(menu_text, menu_text.get_rect(center=menu_btn.center))
    return resume_btn, save_btn, menu_btn


# === ELEMENTOS DE HUD Y MENSAJES ===
def draw_pal_actual(screen, pal_actual):
    """Dibuja la palabra que el usuario está formando actualmente."""
    curr_txt = FONT_MEDIUM.render(pal_actual.upper(), True, TEXT_COLOR)
    screen.blit(curr_txt, (GAME_AREA_WIDTH // 2 - curr_txt.get_width() // 2, HEIGHT - 280))


def draw_score(screen, score):
    """Dibuja el puntaje actual del jugador."""
    score_txt = FONT_MEDIUM.render(f"Puntos: {score}", True, TEXT_COLOR)
    screen.blit(score_txt, (GAME_AREA_WIDTH // 2 - score_txt.get_width() // 2, HEIGHT - 85))


def draw_combo_message(screen, combo_msg, combo_timer):
    """Dibuja el mensaje de combo si está activo."""
    if combo_msg and pygame.time.get_ticks() - combo_timer < COMBO_DURATION_MS:
        msg = FONT_MEDIUM.render(combo_msg, True, FOUND_COLOR)
        screen.blit(msg, (GAME_AREA_WIDTH // 2 - msg.get_width() // 2, HEIGHT - 280))


def draw_time(screen, elapsed_time):
    """Dibuja el tiempo transcurrido de la partida."""
    m, s = divmod(elapsed_time, 60)
    time_txt = FONT_MEDIUM.render(f"Tiempo: {m:02}:{s:02}", True, TEXT_COLOR)
    screen.blit(time_txt, (20, 20))


def draw_word_count(screen, found_count, target_count):
    """Dibuja el contador de palabras halladas vs objetivo."""
    found_txt = FONT_MEDIUM.render(f"Palabras halladas: ({found_count}/{target_count})", True, TEXT_COLOR)
    screen.blit(found_txt, (GAME_AREA_WIDTH // 2 - found_txt.get_width() // 2, HEIGHT // 3 - HEX_RADIUS - 85))


def draw_victory_message(screen):
    """Dibuja el mensaje de victoria cuando el jugador gana."""
    w = FONT_LARGE.render("¡Has ganado!", True, FOUND_COLOR)
    screen.blit(w, (GAME_AREA_WIDTH // 2 - w.get_width() // 2, HEIGHT // 2))


def draw_word_feedback(screen, game_state):
    """Dibuja el mensaje de feedback (bien/mal) tras comprobar una palabra."""
    if hasattr(game_state, 'mensaje_pal') and game_state.mensaje_pal:
        msg, is_ok, ts = game_state.mensaje_pal
        color = FOUND_COLOR if is_ok else (255, 60, 60)
        if pygame.time.get_ticks() - ts < 1200:
            font = FONT_MEDIUM
            text = font.render(msg, True, color)
            rect = text.get_rect(center=(GAME_AREA_WIDTH // 2, HEIGHT - 295))
            pygame.draw.rect(screen, (30,30,30), rect.inflate(30,16), border_radius=8)
            screen.blit(text, rect)