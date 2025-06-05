import pygame
import os
from .constants import *

class FireAnimation:
    def __init__(self):
        self.frames = [
            pygame.image.load(os.path.join(ANIMATIONS_DIR, "fire", f"fuego_{i}.png")).convert_alpha() 
            for i in range(6)
        ]
        self.blue_frames = [
            pygame.image.load(os.path.join(ANIMATIONS_DIR, "fire", f"fuego_azul_{i+1}.png")).convert_alpha()
            for i in range(6)
        ]
        self.violet_frames = [
            pygame.image.load(os.path.join(ANIMATIONS_DIR, "fire", f"violeta{i+1}.png")).convert_alpha()
            for i in range(6)
        ]
        self.current_frame = 0
        self.animation_timer = pygame.time.get_ticks()
        self.active = False

    def update(self, combo_cont):
        # Actualiza el estado de la animación según el combo
        self.active = combo_cont >= 2
        if self.active:
            if pygame.time.get_ticks() - self.animation_timer > 60:
                self.current_frame = (self.current_frame + 1) % 6
                self.animation_timer = pygame.time.get_ticks()
        else:
            self.current_frame = 0  # Opcional: reinicia la animación si no está activa

    def draw(self, screen, combo_cont=None):
        if self.active:
            # Fuego violeta para combo >=10 (x2), azul para 5-9, normal para el resto
            if combo_cont is not None and combo_cont >= 10:
                frames = self.violet_frames
            elif combo_cont is not None and combo_cont >= 5:
                frames = self.blue_frames
            else:
                frames = self.frames
            frame = frames[self.current_frame]
            frame = pygame.transform.scale(frame, (175, 350))
            fire_x = WIDTH - SIDEBAR_WIDTH // 2
            fire_y = HEIGHT - 150  # Posición ajustable
            rect = frame.get_rect(center=(fire_x, fire_y))
            screen.blit(frame, rect)
