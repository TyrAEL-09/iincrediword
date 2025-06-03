import math, pygame, random
from .constants import *
from .word_logic import choose_letters_and_words
from .state_ui import setup_letter_positions, setup_buttons
from .state_logic import (
    is_valid_word,
    handle_combo_and_feedback,
    find_heptacrack,
    force_one_heptacrack
)

class GameState:
    def __init__(self):
        self.raw_letters, self.center_letter, self.valid_words = choose_letters_and_words()
        self.target_count, self.found_words, self.current_word, self.score = len(self.valid_words), [], "", 0
        self.combo_count, self.combo_msg, self.combo_timer, self.paused = 0, "", 0, False
        self.paused_time_total, self.pause_start, self.start_time = 0, 0, pygame.time.get_ticks()
        self.last_word_feedback = None
        force_one_heptacrack(self)
        setup_letter_positions(self)
        setup_buttons(self)
        self.valid_by_initial = {}; [self.valid_by_initial.setdefault(w[0], []).append(w) for w in self.valid_words]

    def is_valid_word(self, word):
        return is_valid_word(self, word)

    def submit_word(self):
        handle_combo_and_feedback(self)

    def delete_last_letter(self): self.current_word = self.current_word[:-1]
    def clear_word(self): self.current_word = ""
    def toggle_pause(self):
        if not self.paused:
            self.paused, self.pause_start, self.current_word = True, pygame.time.get_ticks(), ""
        else:
            self.paused, self.paused_time_total = False, self.paused_time_total + pygame.time.get_ticks() - self.pause_start

    def get_elapsed_time(self):
        t = self.pause_start if self.paused else pygame.time.get_ticks()
        return (t - self.start_time - self.paused_time_total) // 1000

    def is_game_complete(self): return len(self.found_words) >= self.target_count

    def shuffle_letters(self):
        c = self.center_letter
        o = [l for l in self.letters if l != c]
        random.shuffle(o)
        idx = self.letters.index(c)
        self.letters = o[:]; self.letters.insert(idx, c)

    def get_heptacrack(self):
        if not hasattr(self, '_heptacrack'):
            self._heptacrack = find_heptacrack(self)
        return self._heptacrack

    def to_dict(self):
        return {
            "raw_letters": self.raw_letters,
            "center_letter": self.center_letter,
            "valid_words": self.valid_words,
            "target_count": self.target_count,
            "found_words": self.found_words,
            "current_word": self.current_word,
            "score": self.score,
            "combo_count": self.combo_count,
            "combo_msg": self.combo_msg,
            "combo_timer": self.combo_timer,
            "paused": self.paused,
            "paused_time_total": self.paused_time_total,
            "pause_start": self.pause_start,
            "start_time": self.start_time,
            "letters": self.letters,
            "positions": self.positions,
            "valid_by_initial": self.valid_by_initial,
            # Guarda también los botones si quieres restaurar la UI exactamente igual
            "btn_shuffle_rect": self._rect_to_tuple(self.btn_shuffle_rect),
            "btn_check_rect": self._rect_to_tuple(self.btn_check_rect),
            "btn_pause_rect": self._rect_to_tuple(self.btn_pause_rect),
            "btn_del_rect": self._rect_to_tuple(self.btn_del_rect),
            "btn_clear_rect": self._rect_to_tuple(self.btn_clear_rect),
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls.__new__(cls)
        obj.raw_letters = data["raw_letters"]
        obj.center_letter = data["center_letter"]
        obj.valid_words = data["valid_words"]
        obj.target_count = data["target_count"]
        obj.found_words = data["found_words"]
        obj.current_word = data["current_word"]
        obj.score = data["score"]
        obj.combo_count = data["combo_count"]
        obj.combo_msg = data["combo_msg"]
        obj.combo_timer = data["combo_timer"]
        obj.paused = data["paused"]
        obj.paused_time_total = data["paused_time_total"]
        obj.pause_start = data["pause_start"]
        obj.start_time = data["start_time"]
        obj.letters = data["letters"]
        obj.positions = data["positions"]
        obj.valid_by_initial = data["valid_by_initial"]
        # Restaura los botones
        import pygame
        obj.btn_shuffle_rect = cls._tuple_to_rect(data.get("btn_shuffle_rect"))
        obj.btn_check_rect = cls._tuple_to_rect(data.get("btn_check_rect"))
        obj.btn_pause_rect = cls._tuple_to_rect(data.get("btn_pause_rect"))
        obj.btn_del_rect = cls._tuple_to_rect(data.get("btn_del_rect"))
        obj.btn_clear_rect = cls._tuple_to_rect(data.get("btn_clear_rect"))
        # Asegura que last_word_feedback siempre exista
        obj.last_word_feedback = data.get("last_word_feedback", None)
        return obj

    @staticmethod
    def _rect_to_tuple(rect):
        # Convierte un pygame.Rect a tupla para serializar
        return (rect.x, rect.y, rect.width, rect.height) if rect else None

    @staticmethod
    def _tuple_to_rect(t):
        # Convierte una tupla a pygame.Rect
        import pygame
        return pygame.Rect(*t) if t else None