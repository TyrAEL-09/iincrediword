# game/boggle_game.py
import tkinter as tk
from tkinter import PhotoImage
from typing import List, Tuple, Set, Optional, Dict
import pickle # Importar para guardar/cargar
import os # Para verificar si el archivo existe

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
            music_bg_path=self.ui_settings.MUSIC_BACKGROUND,
            sound_winning_path=self.ui_settings.SOUND_WINNING
        )
        self.word_generator = WordGenerator(game_settings=self.game_settings)

        self.menu_ui = MenuUI(self.root, self.ui_settings,
                              on_start_game=self._start_new_game_action, # Cambiado a nueva partida
                              on_music_toggle=self.toggle_music,
                              on_back_menu=self._back_to_menu_action,
                              on_how_to_play_menu_click=lambda: self._create_how_to_play_window("Cómo Jugar - Menú"),
                              on_load_game=self._load_game_action) # Nuevo callback para cargar partida

        self.game_ui = GameUI(self.root, self.ui_settings,
                              on_cell_click=self._on_grid_cell_click,
                              on_submit_word=self.check_word,
                              on_pause_toggle=self.toggle_pause,
                              on_music_toggle=self.toggle_music,
                              on_clear_selection=self._on_clear_button_click,
                              on_how_to_play_game_click=lambda: self._create_how_to_play_window("Cómo Jugar - Juego"),
                              on_back_to_menu_and_save=self._back_to_menu_and_save_action) # Nuevo callback para volver y guardar

        # Game state
        self.current_board: Optional[List[List[str]]] = None
        self.palabras_objetivo: List[str] = []
        self.found_words: Set[str] = set()
        self.score = 0
        self.time_elapsed = 0
        self.timer_running = False
        self.game_active = False # Indica si hay una partida activa

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
        self.menu_ui.enable_start_button() # Habilita ambos botones de inicio
        self.menu_ui.update_music_button_text(self.sound_manager.get_music_status_text())
        self._show_message("", 1)

    def _show_game_interface(self):
        self._set_window_geometry(self.root.winfo_screenwidth() - 100, self.root.winfo_screenheight() - 100)
        self.menu_ui.hide_menu_interface()
        self.game_ui.show_game_interface()
        self.game_ui.update_music_button_text(self.sound_manager.get_music_status_text())

    def _back_to_menu_action(self):
        """Acción de "Volver" genérica al menú principal sin guardar."""
        if self.game_active: # Si hay una partida activa y no se ha guardado, se perderán los datos
            print("Volviendo al menú principal (sin guardar cambios).")
            self._end_game(from_back_to_menu=True) # Finaliza el juego sin guardar
        else:
            print("Volviendo al menú principal (no hay partida activa para guardar).")
            self.game_ui.clear_message() # Asegurar que el mensaje se borre
        self._show_menu_interface()

    def _back_to_menu_and_save_action(self):
        """Acción de "Volver" desde el juego al menú principal, guardando la partida."""
        if self.game_active:
            self._save_game_state()
            self._show_message("Partida guardada y volviendo al menú.", 3000)
            self._end_game(from_back_to_menu=True) # Finaliza el juego después de guardar
        else:
            self._show_message("No hay partida activa para guardar.", 2000)

        self.root.after(3000, self._show_menu_interface) # Esperar a que se muestre el mensaje antes de volver al menú

    # --- Lógica de Guardado/Carga ---
    def _save_game_state(self):
        """Guarda el estado actual del juego en un archivo."""
        game_state = {
            'board': self.current_board,
            'target_words': self.palabras_objetivo,
            'found_words': self.found_words,
            'score': self.score,
            'time_elapsed': self.time_elapsed
        }
        try:
            with open(self.game_settings.SAVE_FILE_NAME, 'wb') as f:
                pickle.dump(game_state, f)
            print(f"Partida guardada exitosamente en {self.game_settings.SAVE_FILE_NAME}")
            self._show_message("Partida guardada exitosamente.", 2000)
        except Exception as e:
            print(f"Error al guardar la partida: {e}")
            self._show_message(f"Error al guardar la partida: {e}", 3000)

    def _load_game_action(self):
        """Carga el estado del juego desde un archivo."""
        if os.path.exists(self.game_settings.SAVE_FILE_NAME):
            try:
                with open(self.game_settings.SAVE_FILE_NAME, 'rb') as f:
                    game_state = pickle.load(f)

                self.current_board = game_state['board']
                self.palabras_objetivo = game_state['target_words']
                self.found_words = game_state['found_words']
                self.score = game_state['score']
                self.time_elapsed = game_state['time_elapsed']

                self._resume_loaded_game()
                self._show_message("Partida cargada exitosamente.", 2000)
                print(f"Partida cargada desde {self.game_settings.SAVE_FILE_NAME}")
            except Exception as e:
                print(f"Error al cargar la partida: {e}")
                self._show_message(f"Error al cargar la partida: {e}", 3000)
                self._show_menu_interface() # Volver al menú si hay error
        else:
            self._show_message("No hay partida guardada para cargar.", 2000)
            print("No se encontró archivo de partida guardada.")


    def _resume_loaded_game(self):
        """Reanuda el juego con el estado cargado."""
        self.game_active = True
        self.timer_running = True
        self._reset_grid_selection() # Limpia cualquier selección previa
        self.game_ui.display_board(self.current_board, self.current_selection_path)
        palabras_por_longitud_para_ui = {}
        for palabra_str in self.palabras_objetivo:
            longitud = len(palabra_str)
            palabras_por_longitud_para_ui.setdefault(longitud, []).append(palabra_str)
        self.game_ui.display_word_list(palabras_por_longitud_para_ui, self.found_words)
        self.game_ui.update_status_labels(len(self.found_words), len(self.palabras_objetivo), self.score)
        self.game_ui.update_timer_label(self._format_time(self.time_elapsed))
        self._show_game_interface()
        self.game_ui.enable_game_controls()
        if self._timer_after_id is not None:
            self.root.after_cancel(self._timer_after_id)
        self._timer_after_id = self.root.after(1000, self._update_timer)

    # --- Lógica del Juego ---
    def _start_new_game_action(self):
        """Prepara e inicia un nuevo juego."""
        self.menu_ui.disable_start_button()
        self._show_message("Cargando palabras y generando tablero...", 0)
        self.root.update()

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
        """Reinicia todas las variables de estado del juego para una nueva partida."""
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
            self.current_selection_path.pop()
            self.current_selected_word = self.current_selected_word[:-1]
        elif (row, col) not in self.current_selection_path:
            is_valid_next_step = False
            if not self.current_selection_path:
                is_valid_next_step = True
            else:
                last_r, last_c = self.current_selection_path[-1]
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
        self.game_ui.update_board_selection(self.current_selection_path)
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
        self.game_ui.update_timer_label(self._format_time(self.time_elapsed))
        self._timer_after_id = self.root.after(1000, self._update_timer)
        self._show_message("Juego Reanudado", 2000)

    def toggle_music(self):
        """Alterna la reproducción de la música de fondo."""
        self.sound_manager.toggle_music()
        music_status_text = self.sound_manager.get_music_status_text()
        self.menu_ui.update_music_button_text(music_status_text)
        self.game_ui.update_music_button_text(music_status_text)

    def clear_entry_input(self):
        """Limpia el texto introducido manualmente en el campo de entrada."""
        self.game_ui.clear_entry()

    def _end_game(self, from_back_to_menu: bool = False):
        """Finaliza el juego, detiene el temporizador y muestra el resumen."""
        self.game_active = False
        self.timer_running = False
        self.clear_entry_input()
        if self._timer_after_id is not None:
            self.root.after_cancel(self._timer_after_id)
            self._timer_after_id = None

        self.game_ui.disable_game_controls()
        if not from_back_to_menu:
            self.sound_manager.play_winning_sound()
            final_message = f"¡Juego Completado!\nPuntuación Final: {self.score}\nTiempo Total: {self._format_time(self.time_elapsed)}"
            self._show_message(final_message, 0)
            self.root.after(5000, self._show_menu_interface)
            self.game_ui.clear_entry()
        else:
            self.game_ui.clear_message()

    def _on_clear_button_click(self):
        """Maneja el evento de clic en el botón 'Limpiar'.
        Borra la selección actual en la matriz y el texto en el campo de entrada.
        """
        if not self.game_active or not self.timer_running: return
        self._reset_grid_selection()
        self.game_ui.clear_entry()

    def _create_how_to_play_window(self, title: str):
        """Crea y muestra la ventana de "Cómo Jugar"."""
        how_to_play_window = tk.Toplevel(self.root)
        how_to_play_window.title(title)
        how_to_play_window.geometry("400x400")
        how_to_play_window.resizable(False, False)
        how_to_play_window.config(bg=self.ui_settings.COLORS['bg'])

        self.root.update_idletasks()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()

        win_width = 400
        win_height = 400

        x = main_x + (main_width // 2) - (win_width // 2)
        y = main_y + (main_height // 2) - (win_height // 2)

        how_to_play_window.geometry(f'{win_width}x{win_height}+{x}+{y}')

        font_ui_tuple = (self.ui_settings.MAIN_FONT_FAMILY, self.ui_settings.UI_FONT_SIZE)
        font_ui_bold_tuple = (self.ui_settings.MAIN_FONT_FAMILY, self.ui_settings.UI_FONT_SIZE, "bold")

        how_to_play_text = """
    ¡Encuentra las 7 palabras que hemos ocultado!

    Cómo Jugar:
    1. Escribe la palabra en el campo de entrada o presiona las casillas de la matriz y presiona "Enviar".
    2. Puedes utilizar cada letra tantas veces como quieras, pero no en la misma palabra.
    3. Las palabras pueden estar en cualquier dirección: horizontal o vertical.
    4. 👁️ ¡OJO! No permitimos diagonales, palabras diagonales.
    5. ¡Disfruta el juego!
        """

        text_label = tk.Label(
            how_to_play_window,
            text=how_to_play_text,
            font=font_ui_tuple,
            bg=self.ui_settings.COLORS['bg'],
            fg=self.ui_settings.COLORS['fg'],
            wraplength=350,
        )
        text_label.pack(padx=10, pady=10, expand=True, fill="both")

        close_button = tk.Button(
            how_to_play_window,
            text="Cerrar",
            command=how_to_play_window.destroy,
            font=font_ui_bold_tuple,
            bg=self.ui_settings.COLORS['button_bg'],
            fg=self.ui_settings.COLORS['button_fg'],
            relief=tk.RAISED,
            borderwidth=2,
            width=10
        )
        close_button.pack(pady=10)

    def run(self):
        """Inicia el bucle principal de la aplicación Tkinter."""
        self.root.mainloop()
