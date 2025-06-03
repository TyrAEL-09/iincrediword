import pygame
import os
from .constants import *
from .ui_elements import draw_pause_screen, is_over_hexagon, hexagon_points
from .sound_utils import play_click_sound, play_feedback_sound, play_combo_sound
from .special_screens import mostrar_confirmacion_salida

def handle_events(game):
    mouse_pos = pygame.mouse.get_pos()
    gs = game.game_state

    if not gs.paused:
        over_btn = any(r.collidepoint(mouse_pos) for r in [
            gs.btn_del_rect, gs.btn_clear_rect, gs.btn_shuffle_rect,
            gs.btn_check_rect, gs.btn_pause_rect
        ])
        over_hex = is_over_hexagon(
            mouse_pos[0], mouse_pos[1],
            gs.positions,
            gs.letters,
            HEX_SIZE
        )
        pygame.mouse.set_cursor(HAND_CURSOR if over_btn or over_hex else ARROW_CURSOR)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                pygame.quit()
                os._exit(0)
            elif event.type == pygame.KEYDOWN:
                gs.combo_msg = ""
                if event.key == pygame.K_RETURN:
                    if gs.current_word.strip() == "":
                        continue
                    prev_feedback = gs.last_word_feedback
                    prev_combo = gs.combo_count
                    gs.submit_word()
                    if gs.last_word_feedback and gs.last_word_feedback != prev_feedback:
                        _, is_ok, _ = gs.last_word_feedback
                        play_feedback_sound(is_ok)
                    if gs.combo_count == 10 and prev_combo < 10:
                        play_combo_sound()
                elif event.key == pygame.K_BACKSPACE:
                    gs.delete_last_letter()
                else:
                    ch = event.unicode.lower()
                    if ch in gs.letters:
                        gs.current_word += ch
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if gs.btn_pause_rect.collidepoint(mouse_pos):
                    play_click_sound()
                    gs.toggle_pause()
                    if gs.paused and game.music_on:
                        pygame.mixer.music.pause()
                    elif not gs.paused and game.music_on:
                        pygame.mixer.music.unpause()
                elif gs.btn_check_rect.collidepoint(mouse_pos):
                    if gs.current_word.strip() == "":
                        continue
                    play_click_sound()
                    prev_feedback = gs.last_word_feedback
                    prev_combo = gs.combo_count
                    gs.submit_word()
                    if gs.last_word_feedback and gs.last_word_feedback != prev_feedback:
                        _, is_ok, _ = gs.last_word_feedback
                        play_feedback_sound(is_ok)
                    if gs.combo_count == 10 and prev_combo < 10:
                        play_combo_sound()
                elif gs.btn_del_rect.collidepoint(mouse_pos):
                    play_click_sound()
                    gs.delete_last_letter()
                elif gs.btn_clear_rect.collidepoint(mouse_pos):
                    play_click_sound()
                    gs.clear_word()
                elif gs.btn_shuffle_rect.collidepoint(mouse_pos):
                    play_click_sound()
                    gs.shuffle_letters()
                elif game.music_btn_rect.collidepoint(mouse_pos):
                    play_click_sound()
                    game.music_on = not game.music_on
                    if game.music_on:
                        pygame.mixer.music.unpause()
                    else:
                        pygame.mixer.music.pause()
                else:
                    for i, letter in enumerate(gs.letters):
                        pts = hexagon_points(gs.positions[i], HEX_SIZE)
                        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                        pygame.draw.polygon(surf, (255, 255, 255), pts)
                        if pygame.mask.from_surface(surf).get_at(mouse_pos):
                            gs.combo_msg = ""
                            gs.current_word += letter
                            break
    else:
        pygame.mouse.set_cursor(HAND_CURSOR)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                pygame.quit()
                os._exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                resume_btn, save_btn, menu_btn = draw_pause_screen(game.screen, mouse_pos)
                if resume_btn.collidepoint(mouse_pos):
                    play_click_sound()
                    gs.toggle_pause()
                    if not gs.paused and game.music_on:
                        pygame.mixer.music.unpause()
                elif save_btn.collidepoint(mouse_pos):
                    play_click_sound()
                    game.guardar_partida()
                elif menu_btn.collidepoint(mouse_pos):
                    play_click_sound()
                    if not game.partida_guardada:
                        # Si no está guardada, muestra el menú de confirmación (guardar y salir, o salir sin guardar)
                        from .special_screens import mostrar_confirmacion_salida
                        mostrar_confirmacion_salida(game)
                        return
                    else:
                        # Si está guardada, vuelve al menú de Hexa-Link (guardar partida, nueva partida, etc.)
                        from menus.menu_hexalink import MenuHexaLink
                        MenuHexaLink(game.usuario, None)
                        game.running = False
                        pygame.quit()
                        return
