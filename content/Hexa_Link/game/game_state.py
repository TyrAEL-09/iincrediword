import math, pygame, random
from .constants import *
from .word_logic import elegir
from .state_ui import setup_letter_posiciones, poner_botones
from .state_logic import (
    word_valida,
    handle_combo_and_feedback,
    find_heptacrack,
    forzar_heptacrack
)

class GameState:
    def __init__(self):
        self.letras_base, self.letra_central, self.pals_validas = elegir()
        self.target_count, self.pal_encontradas, self.pal_actual, self.score = len(self.pals_validas), [], "", 0
        self.combo_cont, self.combo_msg, self.combo_timer, self.pausado = 0, "", 0, False
        self.pausado_time_total, self.pause_start, self.start_time = 0, 0, pygame.time.get_ticks()
        self.mensaje_pal = None
        forzar_heptacrack(self)
        setup_letter_posiciones(self)
        poner_botones(self)
        self.por_inicial = {}; [self.por_inicial.setdefault(w[0], []).append(w) for w in self.pals_validas]

    def word_valida(self, word):
        return word_valida(self, word)

    def submit_word(self):
        handle_combo_and_feedback(self)

    def borrarletra(self): self.pal_actual = self.pal_actual[:-1]
    def clear_word(self): self.pal_actual = ""
    def toggle_pause(self):
        if not self.pausado:
            self.pausado, self.pause_start, self.pal_actual = True, pygame.time.get_ticks(), ""
        else:
            self.pausado, self.pausado_time_total = False, self.pausado_time_total + pygame.time.get_ticks() - self.pause_start

    def get_elapsed_time(self):
        t = self.pause_start if self.pausado else pygame.time.get_ticks()
        return (t - self.start_time - self.pausado_time_total) // 1000

    def is_game_complete(self): return len(self.pal_encontradas) >= self.target_count

    def shuffle_letras(self):
        c = self.letra_central
        o = [l for l in self.letras if l != c]
        random.shuffle(o)
        idx = self.letras.index(c)
        self.letras = o[:]; self.letras.insert(idx, c)

    def get_heptacrack(self):
        if not hasattr(self, '_heptacrack'):
            self._heptacrack = find_heptacrack(self)
        return self._heptacrack

    def to_dict(self):
        return {
            "letras_base": self.letras_base,
            "letra_central": self.letra_central,
            "pals_validas": self.pals_validas,
            "target_count": self.target_count,
            "pal_encontradas": self.pal_encontradas,
            "pal_actual": self.pal_actual,
            "score": self.score,
            "combo_cont": self.combo_cont,
            "combo_msg": self.combo_msg,
            "combo_timer": self.combo_timer,
            "pausado": self.pausado,
            "pausado_time_total": self.pausado_time_total,
            "pause_start": self.pause_start,
            "start_time": self.start_time,
            "letras": self.letras,
            "posiciones": self.posiciones,
            "por_inicial": self.por_inicial,
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
        obj.letras_base = data["letras_base"]
        obj.letra_central = data["letra_central"]
        obj.pals_validas = data["pals_validas"]
        obj.target_count = data["target_count"]
        obj.pal_encontradas = data["pal_encontradas"]
        obj.pal_actual = data["pal_actual"]
        obj.score = data["score"]
        obj.combo_cont = data["combo_cont"]
        obj.combo_msg = data["combo_msg"]
        obj.combo_timer = data["combo_timer"]
        obj.pausado = data["pausado"]
        obj.pausado_time_total = data["pausado_time_total"]
        obj.pause_start = data["pause_start"]
        obj.start_time = data["start_time"]
        obj.letras = data["letras"]
        obj.posiciones = data["posiciones"]
        obj.por_inicial = data["por_inicial"]
        # Restaura los botones
        import pygame
        obj.btn_shuffle_rect = cls._tuple_to_rect(data.get("btn_shuffle_rect"))
        obj.btn_check_rect = cls._tuple_to_rect(data.get("btn_check_rect"))
        obj.btn_pause_rect = cls._tuple_to_rect(data.get("btn_pause_rect"))
        obj.btn_del_rect = cls._tuple_to_rect(data.get("btn_del_rect"))
        obj.btn_clear_rect = cls._tuple_to_rect(data.get("btn_clear_rect"))
        # Asegura que mensaje_pal siempre exista
        obj.mensaje_pal = data.get("mensaje_pal", None)
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