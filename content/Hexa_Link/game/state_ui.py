import math
import pygame
from .constants import *

def setup_letter_positions(game_state):
    o, c = [l for l in game_state.raw_letters if l != game_state.center_letter], game_state.center_letter
    game_state.letters = o[:3] + [c] + o[3:]
    cx, cy, r = GAME_AREA_WIDTH//2, HEIGHT//3, HEX_SIZE*math.sqrt(3)
    ang = [0,60,120,180,240,300]
    game_state.positions = [(cx+r*math.cos(math.radians(a)), cy+r*math.sin(math.radians(a))) for a in ang]
    game_state.positions.insert(3, (cx, cy))

def setup_buttons(game_state):
    cx = GAME_AREA_WIDTH // 2
    comprobar_y = HEIGHT // 3 + 230
    game_state.btn_check_rect = pygame.Rect(cx - 60, comprobar_y, 120, 40)
    fila_y = comprobar_y + 65
    gap = 32
    w, h = 120, 40
    sq = 48
    game_state.btn_del_rect = pygame.Rect(cx - w - gap, fila_y, w, h)
    game_state.btn_shuffle_rect = pygame.Rect(cx - sq//2, fila_y + (h - sq)//2, sq, sq)
    game_state.btn_clear_rect = pygame.Rect(cx + gap, fila_y, w, h)
    pausa_x = GAME_AREA_WIDTH - sq - 20
    pausa_y = 20
    game_state.btn_pause_rect = pygame.Rect(pausa_x, pausa_y, sq, sq)
