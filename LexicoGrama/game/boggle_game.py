# game/boggle_game.py
import tkinter as tk
from tkinter import PhotoImage
from typing import List, Tuple, Set, Optional

from config.settings import GameSettings, UISettings
from utils.sound_manager import SoundManager
from game.word_generator import WordGenerator
from ui.menu_ui import MenuUI
from ui.game_ui import GameUI

class BoggleGame:
    """Clase principal del juego Lexicograma, orquesta los componentes."""

    def __init__(self, archivo_palabras: str, logo_path: str, game_settings: GameSettings, ui_settings: UISettings):
        self.game_settings = game_settings
        self.ui_settings = ui_settings

        self.root = tk.Tk()
        self.root.title("Lexigrama")
        self.root.configure(bg=self.ui_settings.COLORS['bg'])
        try:
            icon_image = PhotoImage(file=self.ui_settings.ICON_PATH)
            self.root.iconphoto(False, icon_image)
        except tk.TclError:
            print(f"Advertencia: No se pudo cargar '{self.ui_settings.ICON_PATH}'. Usando icono por defecto.")

        self.sound_manager = SoundManager(
            sound_correct_path=self.ui_settings.SOUND_CORRECT,
            sound_incorrect_path=self.ui_settings.SOUND_INCORRECT,
            music_bg_path=self.ui_settings.MUSIC_BACKGROUND
        )
        self.word_generator = WordGenerator(game_settings=self.game_settings)

        self.menu_ui = MenuUI(self.root, self.ui_settings,
                              on_start_game=self._start_game_action,
                              on_music_toggle=self.toggle_music,
                              on_back_menu=self._back_to_menu_action)

        self.game_ui = GameUI(self.root, self.ui_settings,
                              on_cell_click=self._on_grid_cell_click,
                              on_submit_word=self.check_word,
                              on_pause_toggle=self.toggle_pause,
                              on_music_toggle=self.toggle_music,
                              on_clear_selection=self._on_clear_button_click) # <-- Nuevo callback aquí

        # Estado del juego
        self.current_board: Optional[List[List[str]]] = None
        self.palabras_objetivo: List[str] = [] # Las palabras que el jugador debe encontrar
        self.found_words: Set[str] = set()
        self.score = 0
        self.time_elapsed = 0
        self.timer_running = False
        self.game_active = False

        self.current_selection_path: List[Tuple[int, int]] = []
        self.current_selected_word: str = ""

        self._timer_after_id: Optional[str] = None
        self._message_after_id: Optional[str] = None

        self._show_menu_interface()
        self.sound_manager.start_music()
        self.menu_ui.update_music_button_text(self.sound_manager.get_music_status_text())
        self.game_ui.update_music_button_text(self.sound_manager.get_music_status_text())


    def _set_window_geometry(self, width: int, height: int):
        """Establece el tamaño y centra la ventana principal."""
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width / 2 - width / 2)
        center_y = int(screen_height / 2 - height / 2)
        self.root.geometry(f'{width}x{height}+{center_x}+{center_y}')

    def _format_time(self, total_seconds: int) -> str:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    # --- Acciones de Interfaz ---
    def _show_menu_interface(self):
        self._set_window_geometry(800, 600)
        self.game_ui.hide_game_interface()
        self.menu_ui.show_menu_interface()
        self.menu_ui.enable_start_button()
        # Actualizar texto del botón de música
        self.menu_ui.update_music_button_text(self.sound_manager.get_music_status_text())
        self._show_message("", 1) # Limpiar cualquier mensaje

    def _show_game_interface(self):
        self._set_window_geometry(self.root.winfo_screenwidth() - 100, self.root.winfo_screenheight() - 100) # Ajustar a un tamaño de juego
        self.menu_ui.hide_menu_interface()
        self.game_ui.show_game_interface()
        # Actualizar texto del botón de música
        self.game_ui.update_music_button_text(self.sound_manager.get_music_status_text())

    def _back_to_menu_action(self):
        """Acción de "Volver" desde cualquier parte al menú principal."""
        print("Volviendo al menú principal.")
        # Reiniciar estado del juego si estaba activo o en pausa
        if self.game_active or not self.timer_running:
            self._end_game(from_back_to_menu=True) # Finalizar el juego para volver al menú
        self._show_menu_interface()

    # --- Lógica del Juego ---
    def _start_game_action(self):
        """Prepara e inicia un nuevo juego."""
        self.menu_ui.disable_start_button()
        self._show_message("Cargando palabras y generando tablero...", 0)
        self.root.update() # Forzar actualización para mostrar el mensaje

        self.current_board = self.word_generator.generate_game_board()
        self.palabras_objetivo = self.word_generator.get_target_words()

        if self.current_board is None or not self.palabras_objetivo or \
           len(self.palabras_objetivo) != self.game_settings.TARGET_WORDS_COUNT:
            msg = "Error: No se pudo generar un tablero válido con las palabras objetivo."
            if not self.word_generator.all_words_by_length:
                msg = f"Error: No se pudo cargar el archivo de palabras '{self.game_settings.WORD_FILE}'."
            print(msg)
            self._show_message(msg, 7000)
            self.menu_ui.enable_start_button()
            self._show_menu_interface()
            return

        self._reset_game_state()
        self.game_ui.display_board(self.current_board, self.current_selection_path)
        # Clasificar palabras objetivo para la UI de lista de pistas
        palabras_por_longitud_para_ui = {}
        for palabra_str in self.palabras_objetivo:
            longitud = len(palabra_str)
            palabras_por_longitud_para_ui.setdefault(longitud, []).append(palabra_str)
        self.game_ui.display_word_list(palabras_por_longitud_para_ui, self.found_words)
        self._show_game_interface()
        self.game_ui.update_status_labels(len(self.found_words), len(self.palabras_objetivo), self.score)
        self._show_message("¡Juego Iniciado! Encuentra las palabras.", 3000)
        print(f"Juego iniciado con {len(self.palabras_objetivo)} palabras en el tablero.")

    def _reset_game_state(self):
        """Reinicia todas las variables de estado del juego."""
        self.found_words.clear()
        self.score = 0
        self.time_elapsed = 0
        self.timer_running = True
        self.game_active = True
        self._reset_grid_selection()
        self.game_ui.update_status_labels(len(self.found_words), len(self.palabras_objetivo), self.score)
        self.game_ui.update_timer_label(self._format_time(0))

        if self._timer_after_id is not None:
            self.root.after_cancel(self._timer_after_id)
        self._timer_after_id = self.root.after(1000, self._update_timer)
        self.game_ui.enable_game_controls()

    def _on_grid_cell_click(self, row: int, col: int, letter: str):
        """Maneja el evento de clic en una celda de la grilla."""
        if not self.game_active or not self.timer_running: return

        if self.current_selection_path and self.current_selection_path[-1] == (row, col):
            # Si se hace clic en la última celda seleccionada, se deselecciona (backtrack)
            self.current_selection_path.pop()
            self.current_selected_word = self.current_selected_word[:-1]
        elif (row, col) not in self.current_selection_path:
            is_valid_next_step = False
            if not self.current_selection_path:
                is_valid_next_step = True # Primera celda de la selección
            else:
                last_r, last_c = self.current_selection_path[-1]
                # Verifica adyacencia (similar a _get_adjacent_cells en WordGenerator)
                adjacents = self.word_generator._get_adjacent_cells(last_r, last_c, self.game_settings.GRID_SIZE[0], self.game_settings.GRID_SIZE[1])
                if (row, col) in adjacents:
                    is_valid_next_step = True
            if is_valid_next_step:
                self.current_selection_path.append((row, col))
                self.current_selected_word += letter

        self.game_ui.update_board_selection(self.current_selection_path)
        self.game_ui.set_entry_text(self.current_selected_word)

    def _reset_grid_selection(self):
        """Reinicia la selección visual de la grilla y el campo de entrada."""
        self.current_selection_path.clear()
        self.current_selected_word = ""
        self.game_ui.update_board_selection(self.current_selection_path) # Descolorear todo
        self.game_ui.clear_entry()

    def check_word(self):
        """Verifica si la palabra ingresada/seleccionada es correcta."""
        if not self.game_active or not self.timer_running: return
        word_input = self.game_ui.get_entered_word()

        if not word_input:
            self._reset_grid_selection()
            return

        if word_input in self.palabras_objetivo and word_input not in self.found_words:
            self._word_found(word_input)
        elif word_input in self.found_words:
            self._show_message(f"'{word_input}' ya fue encontrada.", 2000)
            self.sound_manager.play_incorrect_sound()
        else:
            self._show_message(f"Palabra Incorrecta!", 2000)
            self.sound_manager.play_incorrect_sound()
        self._reset_grid_selection()

    def _word_found(self, word: str):
        """Actualiza el estado del juego cuando se encuentra una palabra."""
        self.found_words.add(word)
        self.game_ui.update_found_word_display(word)

        # Calcular puntuación
        base_score = len(word) * 100
        time_bonus = max(300 - (self.time_elapsed // len(word)), 50)
        word_score = base_score + time_bonus
        self.score += word_score

        self.game_ui.update_status_labels(len(self.found_words), len(self.palabras_objetivo), self.score)
        self.sound_manager.play_correct_sound()
        self._show_message(f"¡Palabra encontrada! +{word_score} puntos", 2500)

        if len(self.found_words) == len(self.palabras_objetivo):
            self._end_game()

    def _show_message(self, message: str, duration: int = 2000):
        """Muestra un mensaje temporal en la interfaz."""
        self.game_ui.show_message(message)
        if self._message_after_id is not None:
            self.root.after_cancel(self._message_after_id)
        if duration > 0:
            self._message_after_id = self.root.after(duration, self.game_ui.clear_message)

    def _update_timer(self):
        """Actualiza el temporizador del juego."""
        if self.timer_running and self.game_active:
            self.time_elapsed += 1
            self.game_ui.update_timer_label(self._format_time(self.time_elapsed))
            self._timer_after_id = self.root.after(1000, self._update_timer)

    def toggle_pause(self):
        """Alterna el estado de pausa del juego."""
        if not self.game_active: return

        if self.timer_running:
            self._pause_game()
        else:
            self._resume_game()

    def _pause_game(self):
        """Pausa el juego y sus elementos."""
        self.timer_running = False
        if self._timer_after_id is not None:
            self.root.after_cancel(self._timer_after_id)
            self._timer_after_id = None
        self.game_ui.disable_game_controls()
        self._show_message("Juego Pausado", 0)

    def _resume_game(self):
        """Reanuda el juego y sus elementos."""
        self.timer_running = True
        self.game_ui.enable_game_controls()
        self.game_ui.update_timer_label(self._format_time(self.time_elapsed)) # Actualizar inmediatamente
        self._timer_after_id = self.root.after(1000, self._update_timer)
        self._show_message("Juego Reanudado", 2000)

    def toggle_music(self):
        """Alterna la reproducción de la música de fondo."""
        self.sound_manager.toggle_music()
        # Actualizar los botones en ambas interfaces
        music_status_text = self.sound_manager.get_music_status_text()
        self.menu_ui.update_music_button_text(music_status_text)
        self.game_ui.update_music_button_text(music_status_text)

    def _end_game(self, from_back_to_menu: bool = False):
        """Finaliza el juego, detiene el temporizador y muestra el resumen."""
        self.game_active = False
        self.timer_running = False
        if self._timer_after_id is not None:
            self.root.after_cancel(self._timer_after_id)
            self._timer_after_id = None

        self.game_ui.disable_game_controls() # Deshabilitar controles al final del juego

        if not from_back_to_menu:
            final_message = f"¡Juego Completado!\nPuntuación Final: {self.score}\nTiempo Total: {self._format_time(self.time_elapsed)}"
            self._show_message(final_message, 0) # Mostrar el mensaje final
            self.root.after(5000, self._show_menu_interface) # Volver al menú después de un retraso
        else:
            self.game_ui.clear_message() # Limpiar mensaje si se vuelve al menú directamente

    def _on_clear_button_click(self):
        """Maneja el evento de clic en el botón 'Limpiar'.
        Borra la selección actual en la matriz y el texto en el campo de entrada.
        """
        if not self.game_active or not self.timer_running: return
        self._reset_grid_selection()
        self.game_ui.clear_entry() # Asegura que el campo de entrada también se borre

    def run(self):
        """Inicia el bucle principal de la aplicación Tkinter."""
        self.root.mainloop()