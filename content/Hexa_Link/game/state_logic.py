import pygame
from .constants import *
from .sound_utils import play_combo_sound  # Corrige el import para evitar el ciclo

def is_valid_word(game_state, word):
    return (
        word in game_state.valid_words and
        game_state.center_letter in word and
        len(word) >= MIN_LETTERS and
        set(word) <= set(game_state.raw_letters)
    )

def handle_combo_and_feedback(game_state):
    prev_combo = game_state.combo_count
    if (
        game_state.current_word and
        game_state.current_word not in game_state.found_words and
        is_valid_word(game_state, game_state.current_word)
    ):
        game_state.combo_count += 1
        mult = max([m for t, m in sorted(COMBO_MULTIPLIERS.items()) if game_state.combo_count >= t] + [1.0])
        game_state.score += int(len(game_state.current_word) * POINTS_PER_LETTER * mult)
        game_state.found_words.append(game_state.current_word)
        game_state.last_word_feedback = ("bien!", True, pygame.time.get_ticks())
        if prev_combo < 10 and game_state.combo_count == 10:
            play_combo_sound()
        if game_state.combo_count >= 2:
            game_state.combo_msg = f"COMBO ACTIVADO: x{mult}, RACHA DE {game_state.combo_count} PALABRAS!"
            game_state.combo_timer = pygame.time.get_ticks()
    else:
        game_state.combo_count = 0
        if game_state.current_word:
            game_state.last_word_feedback = ("fallaste :(", False, pygame.time.get_ticks())
    game_state.current_word = ""

def find_heptacrack(game_state):
    pool = set(game_state.raw_letters)
    for w in game_state.valid_words:
        if set(w) == pool and all(w.count(l) >= 1 for l in pool) and len(w) >= 7:
            return w
    return None

def force_one_heptacrack(game_state):
    pool = set(game_state.raw_letters)
    heptacracks = [w for w in game_state.valid_words if set(w) == pool and all(w.count(l) >= 1 for l in pool) and len(w) >= 7]
    if not heptacracks:
        from Hexa_Link.game.constants import WORDS_FILE
        with open(WORDS_FILE, encoding="utf-8") as f:
            for line in f:
                w = line.strip().upper()
                if set(w) == pool and all(w.count(l) >= 1 for l in pool) and len(w) >= 7:
                    game_state.valid_words.append(w)
                    game_state.valid_by_initial.setdefault(w[0], []).append(w)
                    game_state._heptacrack = w
                    break
    else:
        game_state._heptacrack = heptacracks[0]
        game_state.valid_words = [w for w in game_state.valid_words if w != game_state._heptacrack or w == heptacracks[0]]
        game_state.valid_by_initial = {}
        for w in game_state.valid_words:
            game_state.valid_by_initial.setdefault(w[0], []).append(w)
