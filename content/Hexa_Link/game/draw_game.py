import pygame
import os
from .constants import *
from .ui_elements import (
    draw_word_count,
    draw_hexagons,
    draw_pal_actual,
    draw_game_buttons,
    draw_score,
    draw_combo_message,
    draw_word_feedback,
    draw_sidebar,
    draw_time,
    draw_pause_screen
)
from .special_screens import menu_victoria

def draw_game(game):
    gs = game.game_state
    game.screen.fill(BG_COLOR)
    if not hasattr(game, 'scroll_offset'):
        game.scroll_offset = 0
    if not hasattr(game, 'max_scroll'):
        game.max_scroll = 0
    if not gs.pausado:
        draw_word_count(game.screen, len(gs.pal_encontradas), gs.target_count)
        draw_hexagons(game.screen, gs.posiciones, gs.letras, gs.letra_central, pygame.mouse.get_pos())
        draw_pal_actual(game.screen, gs.pal_actual)
        draw_game_buttons(game.screen, gs, pygame.mouse.get_pos())
        draw_score(game.screen, gs.score)
        draw_combo_message(game.screen, gs.combo_msg, gs.combo_timer)
        draw_word_feedback(game.screen, gs)
        # --- Sidebar con mini-ventana scrolleable ---
        window_y, window_h, words_content_h = draw_sidebar(game.screen, gs.por_inicial, gs.pal_encontradas, gs.get_heptacrack(), game.scroll_offset)
        game.max_scroll = max(0, words_content_h - window_h)
        if game.scroll_offset > game.max_scroll:
            game.scroll_offset = game.max_scroll
        # Guardar área de la mini-ventana y altura de contenido para el handler
        game.last_sidebar_window = (window_y, window_h)
        game.last_sidebar_content_h = words_content_h
        game.fire_animation.draw(game.screen, gs.combo_cont)
        draw_time(game.screen, gs.get_elapsed_time())
        if gs.is_game_complete():
            if game.music_on:
                pygame.mixer.music.stop()
            menu_victoria(game)
            pygame.quit()
            os._exit(0)
            return
        color = CENTER_COLOR if game.music_on else (200, 0, 0)
        pygame.draw.rect(game.screen, color, game.music_boton_rect, border_radius=8)
        if game.music_on:
            icon = "♪"
            font = pygame.font.SysFont('Arial', 32)
            text = font.render(icon, True, (255,255,255))
            text_rect = text.get_rect(center=game.music_boton_rect.center)
            game.screen.blit(text, text_rect)
        else:
            if game.nomusica_img:
                img_rect = game.nomusica_img.get_rect(center=game.music_boton_rect.center)
                game.screen.blit(game.nomusica_img, img_rect)
            else:
                font = pygame.font.SysFont('Arial', 32)
                text = font.render("✕", True, (255,255,255))
                text_rect = text.get_rect(center=game.music_boton_rect.center)
                game.screen.blit(text, text_rect)
        if game.save_message and pygame.time.get_ticks() - game.save_message_timer < 1800:
            font = pygame.font.SysFont('Arial', 22, bold=True)
            text = font.render(game.save_message, True, (0,191,255))
            rect = text.get_rect(center=(WIDTH//2, HEIGHT-40))
            pygame.draw.rect(game.screen, (30,30,30), rect.inflate(30,16), border_radius=8)
            game.screen.blit(text, rect)
        elif game.save_message:
            game.save_message = None
    else:
        draw_pause_screen(game.screen, pygame.mouse.get_pos())
        if game.save_message and pygame.time.get_ticks() - game.save_message_timer < 1800:
            font = pygame.font.SysFont('Arial', 22, bold=True)
            text = font.render(game.save_message, True, (0,191,255))
            rect = text.get_rect(center=(WIDTH//2, HEIGHT-40))
            pygame.draw.rect(game.screen, (30,30,30), rect.inflate(30,16), border_radius=8)
            game.screen.blit(text, rect)
        elif game.save_message:
            game.save_message = None
    pygame.display.flip()
