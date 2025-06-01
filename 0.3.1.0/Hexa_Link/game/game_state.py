import math, pygame, random
from .constants import *
from .word_logic import choose_letters_and_words

class GameState:
    def __init__(self):
        self.raw_letters, self.center_letter, self.valid_words = choose_letters_and_words()
        self.target_count, self.found_words, self.current_word, self.score = len(self.valid_words), [], "", 0
        self.combo_count, self.combo_msg, self.combo_timer, self.paused = 0, "", 0, False
        self.paused_time_total, self.pause_start, self.start_time = 0, 0, pygame.time.get_ticks()
        self._setup_letter_positions(); self._setup_buttons()
        self.valid_by_initial = {}; [self.valid_by_initial.setdefault(w[0], []).append(w) for w in self.valid_words]

    def _setup_letter_positions(self):
        o, c = [l for l in self.raw_letters if l != self.center_letter], self.center_letter
        self.letters = o[:3] + [c] + o[3:]
        cx, cy, r = GAME_AREA_WIDTH//2, HEIGHT//3, HEX_SIZE*math.sqrt(3)
        ang = [0,60,120,180,240,300]
        self.positions = [(cx+r*math.cos(math.radians(a)), cy+r*math.sin(math.radians(a))) for a in ang]
        self.positions.insert(3, (cx, cy))

    def _setup_buttons(self):
        cx = GAME_AREA_WIDTH // 2
        comprobar_y = HEIGHT // 3 + 230  # Subido un poco respecto al anterior
        self.btn_check_rect = pygame.Rect(cx - 60, comprobar_y, 120, 40)
        # Fila inferior: Borrar, Reordenar, Eliminar (simétricos y alineados)
        fila_y = comprobar_y + 65  # Subido un poco respecto al anterior
        gap = 32
        w, h = 120, 40
        sq = 48
        self.btn_del_rect = pygame.Rect(cx - w - gap, fila_y, w, h)
        self.btn_shuffle_rect = pygame.Rect(cx - sq//2, fila_y + (h - sq)//2, sq, sq)
        self.btn_clear_rect = pygame.Rect(cx + gap, fila_y, w, h)
        # Pausa (esquina superior derecha del área de juego)
        pausa_x = GAME_AREA_WIDTH - sq - 20
        pausa_y = 20
        self.btn_pause_rect = pygame.Rect(pausa_x, pausa_y, sq, sq)

    def is_valid_word(self, word):
        return word in self.valid_words and self.center_letter in word and len(word) >= MIN_LETTERS and set(word) <= set(self.raw_letters)

    def submit_word(self):
        if self.current_word and self.current_word not in self.found_words and self.is_valid_word(self.current_word):
            self.combo_count += 1
            mult = max([m for t, m in sorted(COMBO_MULTIPLIERS.items()) if self.combo_count >= t] + [1.0])
            self.score += int(len(self.current_word) * POINTS_PER_LETTER * mult)
            self.found_words.append(self.current_word)
            if self.combo_count >= 2:
                self.combo_msg = f"COMBO ACTIVADO: x{mult}, RACHA DE {self.combo_count} PALABRAS!"
                self.combo_timer = pygame.time.get_ticks()
        else: self.combo_count = 0
        self.current_word = ""

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