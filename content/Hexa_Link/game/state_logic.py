import pygame
from .constants import *
from .sound_utils import sonido_combo 
def word_valida(game_state, word):
    return (
        word in game_state.pals_validas and
        game_state.letra_central in word and
        len(word) >= MIN_letras and
        set(word) <= set(game_state.letras_base)
    )

def handle_combo_and_feedback(game_state):
    combo_actual = game_state.combo_cont
    if (
        game_state.pal_actual and
        game_state.pal_actual not in game_state.pal_encontradas and
        word_valida(game_state, game_state.pal_actual)
    ):
        game_state.combo_cont += 1
        mult = max([m for t, m in sorted(COMBO_MULTIPLIERS.items()) if game_state.combo_cont >= t] + [1.0])
        game_state.score += int(len(game_state.pal_actual) * POINTS_PER_LETTER * mult)
        game_state.pal_encontradas.append(game_state.pal_actual)
        game_state.mensaje_pal = ("bien!", True, pygame.time.get_ticks())
        if combo_actual < 10 and game_state.combo_cont == 10:
            sonido_combo()
        if game_state.combo_cont >= 2:
            game_state.combo_msg = f"COMBO ACTIVADO: x{mult}, RACHA DE {game_state.combo_cont} PALABRAS!"
            game_state.combo_timer = pygame.time.get_ticks()
    else:
        game_state.combo_cont = 0
        if game_state.pal_actual:
            game_state.mensaje_pal = ("no encontrada :(", False, pygame.time.get_ticks())
    game_state.pal_actual = ""

def find_heptacrack(game_state):
    pool = set(game_state.letras_base)
    for w in game_state.pals_validas:
        if set(w) == pool and all(w.count(l) >= 1 for l in pool) and len(w) >= 7:
            return w
    return None

def forzar_heptacrack(game_state):
    pool = set(game_state.letras_base)
    heptacracks = [w for w in game_state.pals_validas if set(w) == pool and all(w.count(l) >= 1 for l in pool) and len(w) >= 7]
    if not heptacracks:
        from Hexa_Link.game.constants import WORDS_FILE
        with open(WORDS_FILE, encoding="utf-8") as f:
            for line in f:
                w = line.strip().upper()
                if set(w) == pool and all(w.count(l) >= 1 for l in pool) and len(w) >= 7:
                    game_state.pals_validas.append(w)
                    game_state.por_inicial.setdefault(w[0], []).append(w)
                    game_state._heptacrack = w
                    break
    else:
        game_state._heptacrack = heptacracks[0]
        game_state.pals_validas = [w for w in game_state.pals_validas if w != game_state._heptacrack or w == heptacracks[0]]
        game_state.por_inicial = {}
        for w in game_state.pals_validas:
            game_state.por_inicial.setdefault(w[0], []).append(w)
