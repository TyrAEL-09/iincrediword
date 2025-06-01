import pygame
import math
import os
from Hexa_Link.game.constants import *
from PIL import Image

def hexagon_points(center, size):
    cx, cy = center
    return [(cx + size * math.cos(math.radians(60*i - 30)), cy + size * math.sin(math.radians(60*i - 30))) for i in range(6)]

def is_over_hexagon(mx, my, positions, letters, hex_size):
    for i in range(len(letters)):
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pts = hexagon_points(positions[i], hex_size)
        pygame.draw.polygon(surf, (255, 255, 255), pts)
        mask = pygame.mask.from_surface(surf)
        if mask.get_at((mx, my)):
            return True
    return False

def draw_hexagons(screen, positions, letters, center_letter, mouse_pos):
    for i, letter in enumerate(letters):
        pts = hexagon_points(positions[i], HEX_SIZE)
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (255, 255, 255), pts)
        hover = pygame.mask.from_surface(surf).get_at(mouse_pos)
        
        hex_color = HOVER_COLOR if hover else (CENTER_COLOR if letter == center_letter else HEX_COLOR)
        pygame.draw.polygon(screen, hex_color, pts)
        
        text_color = (0, 0, 0) if letter == center_letter else TEXT_COLOR
        txt = FONT_LARGE.render(letter.upper(), True, text_color)
        screen.blit(txt, txt.get_rect(center=positions[i]))

def load_ctk_image(path, size):
    # Utilidad para cargar imagen y convertir a pygame.Surface
    img = Image.open(path).convert("RGBA").resize(size, Image.LANCZOS)
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode)

# Carga las imágenes solo una vez
RECURSOS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "recursos")
PAUSA_IMG = load_ctk_image(os.path.join(RECURSOS_DIR, "pausa.png"), (40, 40))
REORDENAR_IMG = load_ctk_image(os.path.join(RECURSOS_DIR, "reordenar.png"), (32, 32))

def draw_buttons(screen, buttons, mouse_pos):
    for rect, label_text, icon in buttons:
        btn_color = CENTER_COLOR  # Azul del centro para todos los botones
        pygame.draw.rect(screen, btn_color, rect, border_radius=BUTTON_RADIUS)
        pygame.draw.rect(screen, CENTER_COLOR, rect, 2, border_radius=BUTTON_RADIUS)
        if icon:
            icon_rect = icon.get_rect(center=rect.center)
            screen.blit(icon, icon_rect)
        else:
            label = FONT_MEDIUM.render(label_text, True, (0, 0, 0))  # Letras negras
            screen.blit(label, label.get_rect(center=rect.center))

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

def draw_sidebar(screen, valid_by_initial, found_words):
    sidebar = pygame.Rect(WIDTH-SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT)
    pygame.draw.rect(screen, SIDEBAR_BG, sidebar)
    y, max_height, fh, maxw = 20, HEIGHT-40, FONT_SMALL.get_height(), SIDEBAR_WIDTH-30

    for ini, lst in sorted(valid_by_initial.items()):
        cnt = sum(w.startswith(ini) for w in found_words)
        found = [w.upper() for w in found_words if w.startswith(ini)]
        if y + fh > max_height: break
        screen.blit(FONT_SMALL.render(f"({cnt}/{len(lst)}) con {ini.upper()}", True, TEXT_COLOR), (WIDTH-SIDEBAR_WIDTH+10, y))
        y += fh
        if found:
            line, lines = "", 0
            for word in found:
                test = (line + ", " if line else "") + word
                if FONT_SMALL.size(test)[0] > maxw:
                    if line:
                        screen.blit(FONT_SMALL.render(line, True, FOUND_COLOR), (WIDTH-SIDEBAR_WIDTH+20, y))
                        y += fh
                        if y + fh > max_height: break
                    line = word
                    lines += 1
                else:
                    line = test
            if line and y + fh <= max_height:
                screen.blit(FONT_SMALL.render(line, True, FOUND_COLOR), (WIDTH-SIDEBAR_WIDTH+20, y))
                y += fh
        y += 5

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

def draw_current_word(screen, current_word):
    curr_txt = FONT_MEDIUM.render(current_word.upper(), True, TEXT_COLOR)
    screen.blit(curr_txt, (GAME_AREA_WIDTH // 2 - curr_txt.get_width() // 2, HEIGHT - 280))

def draw_score(screen, score):
    score_txt = FONT_MEDIUM.render(f"Puntos: {score}", True, TEXT_COLOR)
    screen.blit(score_txt, (GAME_AREA_WIDTH // 2 - score_txt.get_width() // 2, HEIGHT - 85))

def draw_combo_message(screen, combo_msg, combo_timer):
    if combo_msg and pygame.time.get_ticks() - combo_timer < COMBO_DURATION_MS:
        msg = FONT_MEDIUM.render(combo_msg, True, FOUND_COLOR)
        screen.blit(msg, (GAME_AREA_WIDTH // 2 - msg.get_width() // 2, HEIGHT - 280))

def draw_time(screen, elapsed_time):
    m, s = divmod(elapsed_time, 60)
    time_txt = FONT_MEDIUM.render(f"Tiempo: {m:02}:{s:02}", True, TEXT_COLOR)
    screen.blit(time_txt, (20, 20))

def draw_word_count(screen, found_count, target_count):
    found_txt = FONT_MEDIUM.render(f"Palabras halladas: ({found_count}/{target_count})", True, TEXT_COLOR)
    screen.blit(found_txt, (GAME_AREA_WIDTH // 2 - found_txt.get_width() // 2, HEIGHT // 3 - HEX_RADIUS - 85))

def draw_victory_message(screen):
    w = FONT_LARGE.render("¡Has ganado!", True, FOUND_COLOR)
    screen.blit(w, (GAME_AREA_WIDTH // 2 - w.get_width() // 2, HEIGHT // 2))