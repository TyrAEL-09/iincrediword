import tkinter as tk
import pygame
import os
import sys
from typing import List, Tuple, Set, Dict, Optional

# Append project root to sys.path to allow imports from constants, etc.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from constants import LEXICOGRAMA_PALABRAS_FILE, LEXICOGRAMA_SONIDOS_DIR
from . import logic  # Use relative import for local modules
from . import ui     # Use relative import for local modules

# Initialize pygame mixer early
pygame.mixer.init()

class BoggleGame:
    """Coordina el juego Boggle, delegando la lógica a 'logic.py' y la UI a 'ui.py'."""
    
    # Constantes de configuración del juego (pueden moverse a constants.py si se comparten)
    GRID_SIZE = (6, 7)  # filas, columnas
    COLORS = {
        'bg': "#1a1a1a", 'fg': "#ffffff", 'grid': "#333333",
        'button_bg': "#464646", 'button_fg': "#ffffff",
        'grid_cell_bg': "#2c2c2c", 'grid_cell_fg': "#e0e0e0" 
    }
    PALABRAS_OBJETIVO_COUNT = 7 # Renamed from PALABRAS_OBJETIVO to avoid clash with list of words
    DISTRIBUCION_PALABRAS = {
        9: 1, 8: 1, 7: 1, 6: 2, 5: 2
    }

    def __init__(self, root_tk: tk.Tk):
        self.root = root_tk
        self.root.title("LexicoGrama Boggle") # Changed title slightly

        # --- Estado del Juego ---
        self.all_available_words: List[str] = [] # Todas las palabras cargadas del archivo
        self.palabras_objetivo: List[str] = []   # Palabras seleccionadas para ESTA partida
        self.palabras_en_tablero: List[str] = [] # Palabras que SÍ se pudieron insertar en el tablero
        self.palabras_por_longitud: Dict[int, List[str]] = {}
        self.found_words: Set[str] = set()
        
        self.score: int = 0
        self.time_elapsed: int = 0
        self.timer_running: bool = False
        self.game_active: bool = False
        self.paused_time: int = 0 # Stores time_elapsed when paused

        # --- Sonidos ---
        self.sonido_correcto = None
        self.sonido_incorrecto = None
        self.musica_fondo_path = None
        self._load_sounds()
        
        # --- UI ---
        # Pass BoggleGame methods as callbacks to the UI class
        self.ui = ui.BoggleUI(
            self.root, self.COLORS, self.GRID_SIZE,
            iniciar_juego_callback=self.iniciar_juego,
            check_word_callback=self.check_word,
            toggle_pause_callback=self.toggle_pause,
            toggle_music_callback=self.toggle_music
        )
        
        self.all_available_words = logic.cargar_palabras(LEXICOGRAMA_PALABRAS_FILE)
        if not self.all_available_words:
            self.ui.mostrar_mensaje("Error: No se pudo cargar el banco de palabras. El juego no puede iniciar.", error=True, duration=10000)
            self.ui.boton_iniciar.config(state=tk.DISABLED) # Disable start if words fail
        
        self.iniciar_musica_fondo()

    def _load_sounds(self):
        try:
            self.sonido_correcto = pygame.mixer.Sound(os.path.join(LEXICOGRAMA_SONIDOS_DIR, "correcto2.mp3"))
            self.sonido_incorrecto = pygame.mixer.Sound(os.path.join(LEXICOGRAMA_SONIDOS_DIR, "roblox_muerte.mp3"))
            self.musica_fondo_path = os.path.join(LEXICOGRAMA_SONIDOS_DIR, "lofi_sample.mp3")
            print("Sonidos cargados correctamente.")
        except pygame.error as e:
            print(f"Error cargando sonidos: {e}")
            # UI can show a message or sounds will just not play

    def _play_sound(self, sound: Optional[pygame.mixer.Sound]):
        if sound:
            sound.play()

    def iniciar_musica_fondo(self):
        if self.musica_fondo_path and os.path.exists(self.musica_fondo_path):
            try:
                pygame.mixer.music.load(self.musica_fondo_path)
                pygame.mixer.music.play(-1)  # Loop infinito
                pygame.mixer.music.set_volume(0.5) # Default volume
                print("Música de fondo iniciada.")
                self.ui.set_music_button_text("Pausar Música")
            except pygame.error as e:
                print(f"Error reproduciendo música: {e}")
                self.ui.set_music_button_text("Música Error")
        else:
            print("No se encontró el archivo de música de fondo.")
            self.ui.set_music_button_text("No Música")


    def iniciar_juego(self):
        print("Iniciando nuevo juego...")
        if not self.all_available_words:
            self.ui.mostrar_mensaje("Error crítico: Lista de palabras no disponible.", error=True, duration=5000)
            return

        self.palabras_objetivo = logic.seleccionar_palabras_objetivo(
            self.all_available_words, 
            self.DISTRIBUCION_PALABRAS, 
            self.PALABRAS_OBJETIVO_COUNT
        )

        if len(self.palabras_objetivo) < self.PALABRAS_OBJETIVO_COUNT:
            msg = f"Advertencia: Solo se seleccionaron {len(self.palabras_objetivo)}/{self.PALABRAS_OBJETIVO_COUNT} palabras."
            print(msg)
            self.ui.mostrar_mensaje(msg, duration=3000)
            if not self.palabras_objetivo: # No words selected, critical
                 self.ui.mostrar_mensaje("Error: No se pudieron seleccionar palabras para el juego.", error=True, duration=5000)
                 return


        tablero_generado, self.palabras_en_tablero = logic.generar_sopa_letras(
            self.palabras_objetivo, 
            self.GRID_SIZE,
            self.PALABRAS_OBJETIVO_COUNT # Pass how many words we ideally want on the board
        )
        
        if not tablero_generado or not self.palabras_en_tablero:
            self.ui.mostrar_mensaje("Error: No se pudo generar el tablero de juego.", True, 5000)
            # Consider allowing game to start with fewer words if some were placed
            # For now, require tablero_generado and at least one palabra_en_tablero
            if not self.palabras_en_tablero: return

        self.palabras_por_longitud = logic.clasificar_palabras_por_longitud(self.palabras_en_tablero)
        
        # Reset game state
        self.found_words.clear()
        self.score = 0
        self.time_elapsed = 0
        self.timer_running = True
        self.game_active = True
        
        # Update UI
        self.ui.mostrar_tablero(tablero_generado)
        self.ui.hint_labels = self.ui.mostrar_lista_palabras(self.palabras_por_longitud, self.found_words) # Store hint_labels
        self.ui.actualizar_estado(len(self.found_words), len(self.palabras_en_tablero), self.score)
        self.ui.actualizar_timer(f"{self.time_elapsed}s")
        self.ui.mostrar_mensaje("") # Clear any previous messages
        self.ui.mostrar_interfaz_juego(mostrar_input=True)
        self.ui.configurar_estado_juego_activo(True)
        self.ui.configurar_estado_pausa(pausado=False)


        # Start timer only if not already running from a previous game that wasn't properly stopped
        if hasattr(self, "_timer_after_id"):
             self.root.after_cancel(self._timer_after_id)
        self._update_timer()
        
        print(f"Juego iniciado. Palabras en tablero: {len(self.palabras_en_tablero)}.")
        # For debugging: print actual words
        # for longitud, palabras in self.palabras_por_longitud.items():
        #     print(f"  {longitud} letras: {palabras}")


    def check_word(self):
        if not self.game_active or not self.timer_running:
            return
        
        word_ingresada = self.ui.get_entry_value() # Gets value and clears entry
        
        status = logic.verificar_palabra(word_ingresada, self.palabras_en_tablero, self.found_words)
        word_upper = word_ingresada.strip().upper()

        if status == "VALIDA":
            self.found_words.add(word_upper)
            self.ui.revelar_palabra_encontrada(word_upper) # Pass word_upper to match key in hint_labels
            
            word_score = logic.calcular_puntuacion_palabra(word_upper, self.time_elapsed)
            self.score += word_score
            
            self._play_sound(self.sonido_correcto)
            self.ui.mostrar_mensaje(f"¡'{word_upper}' encontrada! +{word_score} puntos")
            
            if len(self.found_words) == len(self.palabras_en_tablero):
                self._end_game(victoria=True)
        elif status == "YA_ENCONTRADA":
            self._play_sound(self.sonido_incorrecto) # Optional: different sound for already found
            self.ui.mostrar_mensaje(f"'{word_upper}' ya fue encontrada.", error=True)
        elif status == "INVALIDA":
            self._play_sound(self.sonido_incorrecto)
            self.ui.mostrar_mensaje(f"'{word_upper}' no está en la lista.", error=True)
        # No action for "VACIA" as entry is cleared by get_entry_value

        self.ui.actualizar_estado(len(self.found_words), len(self.palabras_en_tablero), self.score)

    def _update_timer(self):
        if self.timer_running:
            self.time_elapsed += 1
            self.ui.actualizar_timer(f"{self.time_elapsed}s")
            # Store after_id to be able to cancel it if game restarts
            self._timer_after_id = self.root.after(1000, self._update_timer)

    def toggle_pause(self):
        if not self.game_active: # Don't allow pause if game hasn't started or has ended
            return

        self.timer_running = not self.timer_running
        if self.timer_running: # Resuming
            self.time_elapsed = self.paused_time # Restore time from when paused
            self._update_timer() # Restart the timer loop
            self.ui.mostrar_mensaje("Juego reanudado.")
        else: # Pausing
            if hasattr(self, "_timer_after_id"): # Cancel the scheduled _update_timer
                self.root.after_cancel(self._timer_after_id)
            self.paused_time = self.time_elapsed # Save current time
            self.ui.mostrar_mensaje("Juego pausado.", duration=0) # Persistent message
            
        self.ui.configurar_estado_pausa(not self.timer_running) # UI update reflects new state

    def toggle_music(self):
        if not self.musica_fondo_path: return

        if pygame.mixer.music.get_busy(): # Music is playing
            pygame.mixer.music.pause()
            self.ui.set_music_button_text("Reanudar Música")
        else: # Music is paused or stopped
            pygame.mixer.music.unpause() # Or play if it was fully stopped and you want restart
            self.ui.set_music_button_text("Pausar Música")
            # If music was stopped (not just paused), you might need to pygame.mixer.music.play(-1) again.
            # For simplicity, this assumes unpause is sufficient.

    def _end_game(self, victoria: bool):
        self.game_active = False
        self.timer_running = False
        if hasattr(self, "_timer_after_id"):
             self.root.after_cancel(self._timer_after_id)

        self.ui.configurar_estado_juego_activo(False)
        self.ui.configurar_estado_pausa(False) # Ensure pause button is reset
        self.ui.mostrar_interfaz_juego(mostrar_input=False) # Hide game inputs, show start

        if victoria:
            final_message = f"¡Felicidades! Todas las palabras encontradas. Puntuación final: {self.score}"
        else: # Could be called by a timeout in future, or manual game over
            final_message = f"Juego terminado. Puntuación final: {self.score}"
        
        self.ui.mostrar_mensaje(final_message, duration=10000) # Longer message display
        print(final_message)

    def run(self):
        """Ejecuta el bucle principal de Tkinter."""
        self.root.mainloop()

def iniciar_lexicograma(usuario: Optional[str] = None): # Added usuario to match expected signature
    """Función de entrada para iniciar el juego LexicoGrama."""
    print(f"Iniciando LexicoGrama para el usuario: {usuario if usuario else 'Invitado'}")
    root = tk.Tk()
    # Consider adding geometry settings for the window if desired
    # root.geometry("800x600") 
    game_instance = BoggleGame(root)
    game_instance.run()

# Punto de entrada principal, si se ejecuta este archivo directamente
if __name__ == "__main__":
    iniciar_lexicograma("TestUser")
```
