# sound_manager.py
import pygame

class SoundManager:
    """Gestiona la reproducción de efectos de sonido y música de fondo."""

    def __init__(self, sound_correct_path: str, sound_incorrect_path: str, music_bg_path: str, 
                       sound_winning_path: str):
        self._sound_correct = self._load_sound(sound_correct_path)
        self._sound_incorrect = self._load_sound(sound_incorrect_path)
        self._sound_winning = self._load_sound(sound_winning_path)
        self._music_bg_path = music_bg_path
        self._music_pausado_by_system = False

    def _load_sound(self, path: str):
        """Carga un archivo de sonido."""
        try:
            return pygame.mixer.Sound(path)
        except pygame.error as e:
            print(f"Error cargando sonido '{path}': {e}")
            return None

    def play_correct_sound(self):
        """Reproduce el sonido de respuesta correcta."""
        if self._sound_correct:
            self._sound_correct.play()

    def play_incorrect_sound(self):
        """Reproduce el sonido de respuesta incorrecta."""
        if self._sound_incorrect:
            self._sound_incorrect.play()

    def play_winning_sound(self):
        """Reproduce un sonido al finalizar el juego."""
        if self._sound_winning:
            self._sound_winning.play()

    def start_music(self):
        """Inicia la reproducción de la música de fondo en bucle."""
        if self._music_bg_path:
            try:
                pygame.mixer.music.load(self._music_bg_path)
                pygame.mixer.music.play(-1)
                print("Música de fondo iniciada.")
                self._music_pausado_by_system = False
            except pygame.error as e:
                print(f"Error reproduciendo música: {e}")
        else:
            print("No se ha configurado la ruta de la música de fondo.")

    def pause_music(self):
        """Pausa la música de fondo."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self._music_pausado_by_system = True
            print("Música de fondo pausada.")

    def unpause_music(self):
        """Reanuda la música de fondo."""
        if self._music_pausado_by_system:
            pygame.mixer.music.unpause()
            self._music_pausado_by_system = False
            print("Música de fondo reanudada.")
        elif not pygame.mixer.music.get_busy() and self._music_bg_path:
            # Si no estaba en pausa (se detuvo o no se inició), la inicia
            self.start_music()

    def toggle_music(self) -> bool:
        """Alterna el estado de la música (ON/OFF). Retorna True si está sonando."""
        if not self._music_bg_path:
            return False # No hay música que alternar

        if pygame.mixer.music.get_busy():
            self.pause_music()
            return False
        else:
            # Si no está sonando y no está pausada, la inicia. Si está pausada, la reanuda.
            if self._music_pausado_by_system:
                self.unpause_music()
            else:
                self.start_music()
            return pygame.mixer.music.get_busy() # Retorna el estado actual

    def is_music_playing(self) -> bool:
        """Verifica si la música está sonando."""
        return pygame.mixer.music.get_busy()

    def get_music_status_text(self) -> str:
        """Devuelve un texto descriptivo del estado de la música."""
        if not self._music_bg_path:
            return "Música: N/A"
        elif pygame.mixer.music.get_busy():
            return "Música: ON"
        elif self._music_pausado_by_system:
            return "Música: OFF"
        else:
            return "Música: OFF"

    def stop_music(self):
        """Detiene la música de fondo si está sonando."""
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass