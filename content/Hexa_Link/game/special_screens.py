import pygame
import os
from .constants import FONT_PATH

def menu_victoria(game):
    # --- APAGAR LA MUSICA DE FONDO ---
    
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()


    scores = game.guardar_puntaje()
    running = True
    WIDTH, HEIGHT = game.screen.get_size()
    FONT_LARGE = pygame.font.SysFont('Arial', 32, bold=True)
    FONT_MEDIUM = pygame.font.SysFont('Arial', 24, bold=True)
    CENTER_COLOR = (0, 191, 255)
    BUTTON_COLOR = (30, 42, 56)
    BUTTON_RADIUS = 12
    board_w, board_h = 500, 340

    while running:
        game.screen.fill((30, 42, 56))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,120))
        game.screen.blit(overlay, (0, 0))

        title = FONT_LARGE.render("¡Felicidades! Partida completada!", True, CENTER_COLOR)
        title_rect = title.get_rect(center=(WIDTH//2, 80))
        msg_bg = title_rect.inflate(40, 40)
        pygame.draw.rect(game.screen, (30, 42, 56), msg_bg, border_radius=10)
        pygame.draw.rect(game.screen, CENTER_COLOR, msg_bg, 2, border_radius=10)
        game.screen.blit(title, title_rect)

        score_txt = FONT_MEDIUM.render(f"Tu puntuación: {game.game_state.score}", True, (255,255,255))
        score_rect = score_txt.get_rect(center=(WIDTH//2, 140))
        game.screen.blit(score_txt, score_rect)

        board_rect = pygame.Rect(WIDTH//2 - board_w//2, 180, board_w, board_h)
        pygame.draw.rect(game.screen, CENTER_COLOR, board_rect, border_radius=16)
        pygame.draw.rect(game.screen, (255,255,255), board_rect, 2, border_radius=16)
        board_title = FONT_MEDIUM.render("Top 10 Puntajes", True, (255,255,255))
        game.screen.blit(board_title, board_title.get_rect(center=(WIDTH//2, 210)))
        y0 = 240
        for idx, entry in enumerate(scores):
            usuario = entry["usuario"]
            puntaje = entry["score"]
            color = (255,255,255) if idx != 0 else (255, 215, 0)
            txt = FONT_MEDIUM.render(f"{idx+1}. {usuario} - {puntaje}", True, color)
            game.screen.blit(txt, (WIDTH//2 - board_w//2 + 30, y0 + idx*28))

        btn_width, btn_height = 420, 54
        boton_rect = pygame.Rect(WIDTH//2 - btn_width//2, 180+board_h+30, btn_width, btn_height) #Define la posición y el tamaño del botón en la pantalla 
        mouse_pos = pygame.mouse.get_pos()
        btn_color = CENTER_COLOR if boton_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(game.screen, btn_color, boton_rect, border_radius=BUTTON_RADIUS)
        pygame.draw.rect(game.screen, CENTER_COLOR, boton_rect, 2, border_radius=BUTTON_RADIUS)
        btn_label = FONT_MEDIUM.render("Volver al menú de selección de juegos", True, (255,255,255))
        game.screen.blit(btn_label, btn_label.get_rect(center=boton_rect.center))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                game.running = False
                pygame.quit()
                os._exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if boton_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    os._exit(0)
                    # Si quieres volver al menú en vez de cerrar, comenta la línea anterior y descomenta las siguientes:
                    # from menus.seleccion_juego import iniciar_menu
                    # iniciar_menu(game.usuario)
                    # return

def mostrar_confirmacion_salida(game):
    running = True
    WIDTH, HEIGHT = game.screen.get_size()
    import pygame
    pygame.font.init()
    FONT_LARGE = pygame.font.Font(FONT_PATH, 48)
    FONT_MEDIUM = pygame.font.Font(FONT_PATH, 24)
    CENTER_COLOR = (0, 191, 255)
    BUTTON_COLOR = (30, 42, 56)
    BUTTON_RADIUS = 12

    while running:
        game.screen.fill((30, 42, 56))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,120))
        game.screen.blit(overlay, (0, 0))
        title = FONT_LARGE.render("La partida actual no se ha guardado", True, CENTER_COLOR)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 60))
        msg_bg = title_rect.inflate(40, 40)
        pygame.draw.rect(game.screen, (30, 42, 56), msg_bg, border_radius=10)
        pygame.draw.rect(game.screen, CENTER_COLOR, msg_bg, 2, border_radius=10)
        game.screen.blit(title, title_rect)
        msg2 = FONT_MEDIUM.render("¿Deseas salir de todos modos?", True, (255,255,255))
        game.screen.blit(msg2, msg2.get_rect(center=(WIDTH//2, HEIGHT//2 - 10)))
        btn_w, btn_h = 220, 48
        btn1 = pygame.Rect(WIDTH//2 - btn_w - 20, HEIGHT//2 + 40, btn_w, btn_h)
        btn2 = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 40, btn_w, btn_h)
        mouse_pos = pygame.mouse.get_pos()
        color1 = CENTER_COLOR if btn1.collidepoint(mouse_pos) else BUTTON_COLOR
        color2 = CENTER_COLOR if btn2.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(game.screen, color1, btn1, border_radius=BUTTON_RADIUS)
        pygame.draw.rect(game.screen, CENTER_COLOR, btn1, 2, border_radius=BUTTON_RADIUS)
        pygame.draw.rect(game.screen, color2, btn2, border_radius=BUTTON_RADIUS)
        pygame.draw.rect(game.screen, CENTER_COLOR, btn2, 2, border_radius=BUTTON_RADIUS)
        label1 = FONT_MEDIUM.render("Salir y guardar", True, (255,255,255))
        label2 = FONT_MEDIUM.render("Salir y no guardar", True, (255,255,255))
        game.screen.blit(label1, label1.get_rect(center=btn1.center))
        game.screen.blit(label2, label2.get_rect(center=btn2.center))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                game.running = False
                pygame.quit()
                os._exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn1.collidepoint(mouse_pos):
                    game.guardar_partida()
                    game.running = False
                    running = False
                    import pygame
                    pygame.display.quit()
                    pygame.quit()
                    from menus.menu_hexalink import MenuHexaLink
                    MenuHexaLink(game.usuario, None)
                    return
                elif btn2.collidepoint(mouse_pos):
                    game.running = False
                    running = False
                    import pygame
                    pygame.display.quit()
                    pygame.quit()
                    from menus.menu_hexalink import MenuHexaLink
                    MenuHexaLink(game.usuario, None)
                    return
