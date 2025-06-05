import pygame
import os
from .constants import *
from .ui_elements import draw_pause_screen, is_over_hexagon, hexagon_points, point_in_hexagon
from .sound_utils import sonido_click, play_feedback_sound, sonido_combo
from .special_screens import mostrar_confirmacion_salida
from .constants import MUSIC_PATH

def handle_events(game):
    mouse_pos = pygame.mouse.get_pos()
    gs = game.game_state

    # --- Scroll de la mini-ventana de palabras halladas ---
    if not hasattr(game, 'scroll_offset'):
        game.scroll_offset = 0
    if not hasattr(game, 'max_scroll'):
        game.max_scroll = 0
    
    window_y = 0
    window_h = 0
    if hasattr(game, 'last_sidebar_window'):
        window_y, window_h = game.last_sidebar_window

    events = pygame.event.get()  # Obtener eventos una vez por frame

    # Procesar MOUSEWHEEL globalmente (fuera de la distinción pausado/no pausado si es necesario)
    for event in events:
        if event.type == pygame.MOUSEWHEEL:
            if window_h > 0 and hasattr(game, 'last_sidebar_content_h'): # Solo si hay contenido para scrollear
                sidebar_x_start = WIDTH - SIDEBAR_WIDTH + 8 # Ajustar según el área real de la lista de palabras
                sidebar_x_end = WIDTH - 16
                if sidebar_x_start <= mouse_pos[0] <= sidebar_x_end and \
                   window_y <= mouse_pos[1] <= window_y + window_h:
                    
                    game.scroll_offset -= event.y * 30  # Ajustar sensibilidad del scroll
                    if game.scroll_offset < 0:
                        game.scroll_offset = 0
                    

                    if hasattr(game, 'max_scroll') and game.scroll_offset > game.max_scroll:
                        game.scroll_offset = game.max_scroll

    if not gs.pausado:
        # Lógica de cursor y eventos cuando el juego NO está pausado
        over_btn = any(r.collidepoint(mouse_pos) for r in [
            gs.btn_del_rect, gs.btn_clear_rect, gs.btn_shuffle_rect,
            gs.btn_check_rect, gs.btn_pause_rect
        ] if r is not None) # Verificar que los rects no sean None
        
        over_hex = False
        if gs.posiciones and gs.letras:
            over_hex = is_over_hexagon(
                mouse_pos[0], mouse_pos[1],
                gs.posiciones,
                gs.letras,
                HEX_SIZE
            )
        
        pygame.mouse.set_cursor(HAND_CURSOR if over_btn or over_hex else ARROW_CURSOR)

        for event in events:
            if event.type == pygame.QUIT:
                game.running = False
                pygame.quit()
                os._exit(0)
            elif event.type == pygame.KEYDOWN:
                gs.combo_msg = ""
                if event.key == pygame.K_RETURN:
                    if gs.pal_actual.strip() == "":
                        continue
                    prev_feedback = gs.mensaje_pal
                    combo_actual = gs.combo_cont
                    gs.submit_word()
                    if gs.mensaje_pal and gs.mensaje_pal != prev_feedback:
                        _, is_ok, _ = gs.mensaje_pal
                        play_feedback_sound(is_ok)
                    if gs.combo_cont == 10 and combo_actual < 10:
                        sonido_combo()
                elif event.key == pygame.K_BACKSPACE:
                    gs.borrarletra()
                else:
                    ch = event.unicode.lower()
                    if ch in gs.letras: # Comprobar si la letra está en las disponibles
                        gs.pal_actual += ch
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if gs.btn_pause_rect and gs.btn_pause_rect.collidepoint(mouse_pos):
                    sonido_click()
                    gs.toggle_pause()
                    if gs.pausado and game.music_on:
                        pygame.mixer.music.pause()
                    # No es necesario un unpause aquí, se maneja al salir de pausa

                elif gs.btn_check_rect and gs.btn_check_rect.collidepoint(mouse_pos):
                    if gs.pal_actual.strip() == "":
                        continue
                    sonido_click()
                    prev_feedback = gs.mensaje_pal
                    combo_actual = gs.combo_cont
                    gs.submit_word()
                    if gs.mensaje_pal and gs.mensaje_pal != prev_feedback:
                        _, is_ok, _ = gs.mensaje_pal
                        play_feedback_sound(is_ok)
                    if gs.combo_cont == 10 and combo_actual < 10:
                        sonido_combo()
                elif gs.btn_del_rect and gs.btn_del_rect.collidepoint(mouse_pos):
                    sonido_click()
                    gs.borrarletra()
                elif gs.btn_clear_rect and gs.btn_clear_rect.collidepoint(mouse_pos):
                    sonido_click()
                    gs.clear_word()
                elif gs.btn_shuffle_rect and gs.btn_shuffle_rect.collidepoint(mouse_pos):
                    sonido_click()
                    gs.shuffle_letras()
                elif hasattr(game, 'music_boton_rect') and game.music_boton_rect.collidepoint(mouse_pos):
                    sonido_click()
                    game.music_on = not game.music_on
                    if game.music_on:
                        if pygame.mixer.music.get_busy(): # Si ya está sonando (pausada), reanuda
                             pygame.mixer.music.unpause()
                        else: # Si no estaba sonando, la carga y reproduce
                             try:
                                 pygame.mixer.music.load(MUSIC_PATH) 
                                 pygame.mixer.music.play(-1, fade_ms=1000)
                             except pygame.error as e:
                                 print(f"Error al cargar o reproducir música: {e}")
                    else:
                        pygame.mixer.music.fadeout(500) 
                else:
                    if gs.posiciones and gs.letras: 
                        for i, letter in enumerate(gs.letras):
                            pts = hexagon_points(gs.posiciones[i], HEX_SIZE)
                            if point_in_hexagon(mouse_pos, pts):
                                gs.combo_msg = ""
                                gs.pal_actual += letter
                                break
    else: # gs.pausado is True
        pygame.mouse.set_cursor(HAND_CURSOR) # Usar cursor de mano sobre los botones de pausa
        for event in events:
            if event.type == pygame.QUIT:
                game.running = False
                pygame.quit()
                os._exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                resume_btn, save_btn, menu_btn = draw_pause_screen(game.screen, mouse_pos)

                if resume_btn.collidepoint(mouse_pos):
                    sonido_click()
                    gs.toggle_pause()
                    if not gs.pausado and game.music_on: # Si se reanuda y la música estaba activa
                        pygame.mixer.music.unpause()
                elif save_btn.collidepoint(mouse_pos):
                    sonido_click()
                    game.guardar_partida() 
                                        
                elif menu_btn.collidepoint(mouse_pos):
                    sonido_click()
                    if not game.partida_guardada:
                        from .special_screens import mostrar_confirmacion_salida
                        mostrar_confirmacion_salida(game)
                        return
                    else: # Partida SÍ está guardada y se presiona "Volver al menú principal"
                        game.running = False      # 1. Indica al bucle principal del juego que debe terminar.

                        # 2. Cierra explícitamente la ventana de Pygame y desinicializa los módulos de Pygame.
                        pygame.display.quit()     # Cierra la ventana/pantalla de Pygame.
                        pygame.quit()             # Desinicializa todos los módulos de Pygame.

                        # 3. Ahora que Pygame está completamente cerrado, crea la instancia del menú principal.
                        from menus.menu_hexalink import MenuHexaLink # Importación local para evitar ciclos si es necesario
                        MenuHexaLink(game.usuario, None)
                        return 


            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sonido_click()
                    gs.toggle_pause()
                    if not gs.pausado and game.music_on:
                        pygame.mixer.music.unpause()