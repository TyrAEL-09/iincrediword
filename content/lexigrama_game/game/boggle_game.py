# game/boggle_game.py
import tkinter as tk
from tkinter import PhotoImage
from typing import List, Tuple, Set, Optional, Dict
import pickle 
import os 
import json # Importado para la nueva lógica de guardado/carga
import pygame # Importado en pasos anteriores

from config.settings import GameSettings, UISettings
from utils.sound_manager import SoundManager
from game.word_generator import WordGenerator
from ui.menu_ui import MenuUI
from ui.game_ui import GameUI

class BoggleGame:
    """Clase principal del juego Lexicograma, orquesta los componentes."""

    def __init__(self, username: str, archivo_palabras: str, logo_path: str, game_settings: GameSettings, ui_settings: UISettings): # MODIFICADO
        pygame.init() # Inicializa Pygame

        self.game_settings = game_settings
        self.ui_settings = ui_settings
        self.username = username # AÑADIDO

        self.root = tk.Tk()
        self.root.title("Lexigrama")
        self.root.configure(bg=self.ui_settings.COLORS['bg'])
        try:
            # Asegurarse que ICON_PATH sea una cadena o un objeto Path antes de pasarlo a PhotoImage
            icon_path_str = str(self.ui_settings.ICON_PATH)
            icon_image = PhotoImage(file=icon_path_str)
            self.root.iconphoto(False, icon_image)
        except tk.TclError:
            print(f"Advertencia: No se pudo cargar '{self.ui_settings.ICON_PATH}'. Usando icono por defecto.")
        except Exception as e:
            print(f"Error al cargar el icono '{self.ui_settings.ICON_PATH}': {e}. Usando icono por defecto.")


        self.sound_manager = SoundManager(
            sound_correct_path=str(self.ui_settings.SOUND_CORRECT), # Convertir a str por si es Path
            sound_incorrect_path=str(self.ui_settings.SOUND_INCORRECT), # Convertir a str
            music_bg_path=str(self.ui_settings.MUSIC_BACKGROUND), # Convertir a str
            sound_winning_path=str(self.ui_settings.SOUND_WINNING) # Convertir a str
        )
        self.word_generator = WordGenerator(game_settings=self.game_settings)

        self.menu_ui = MenuUI(self.root, self.ui_settings,
                                on_start_game=self._start_new_game_action,
                                on_music_toggle=self.toggle_music,
                                on_back_menu=self._back_to_menu_action,
                                on_how_to_play_menu_click=lambda: self._create_how_to_play_window("Como Jugar Lexigrama"),
                                on_load_game=self._load_game_action) 

        self.game_ui = GameUI(self.root, self.ui_settings,
                                on_cell_click=self._on_grid_cell_click,
                                on_submit_word=self.check_word,
                                on_pause_toggle=self.toggle_pause,
                                on_music_toggle=self.toggle_music,
                                on_clear_selection=self._on_clear_button_click,
                                on_how_to_play_game_click=lambda: self._create_how_to_play_window("Como Jugar Lexigrama"),
                                on_back_to_menu_and_save=self._back_to_menu_and_save_action)

        # Game state
        self.current_board: Optional[List[List[str]]] = None
        self.palabras_objetivo: List[str] = []
        self.found_words: Set[str] = set()
        self.score = 0
        self.time_elapsed = 0
        self.timer_running = False
        self.game_active = False 

        self.current_selection_path: List[Tuple[int, int]] = []
        self.current_selected_word: str = ""

        self._timer_after_id: Optional[str] = None
        self._message_after_id: Optional[str] = None
        
        # self.username = None # ELIMINADO/REEMPLAZADO

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
        self.menu_ui.update_music_button_text(self.sound_manager.get_music_status_text())
        self._show_message("", 1)
        # La lógica de pedir username con input() se elimina
        if not self.username:
             print("Advertencia: Nombre de usuario no establecido al mostrar menú. El guardado/carga podría no funcionar como se espera.")


    def _show_game_interface(self):
        self._set_window_geometry(self.root.winfo_screenwidth() - 100, self.root.winfo_screenheight() - 100)
        self.menu_ui.hide_menu_interface()
        self.game_ui.show_game_interface()
        self.game_ui.update_music_button_text(self.sound_manager.get_music_status_text())

    def _back_to_menu_action(self):
        """Acción de "Volver" genérica al menú principal sin guardar."""
        if self.game_active: 
            print("Volviendo al menú principal (sin guardar cambios).")
            self._end_game(from_back_to_menu=True) 
        else:
            print("Volviendo al menú principal (no hay partida activa para guardar).")
            self.game_ui.clear_message() 
        self._show_menu_interface()

    def _back_to_menu_and_save_action(self):
        """Acción de "Volver" desde el juego al menú principal, guardando la partida."""
        if self.game_active:
            self._save_game_state() 
            self._show_message("Partida guardada y volviendo al menú.", 3000) # MODIFICADO el mensaje
            self._end_game(from_back_to_menu=True) 
        else:
            self._show_message("No hay partida activa para guardar.", 2000)

        self.root.after(3000, self._show_menu_interface) 

    # --- Lógica de Guardado/Carga ---
    # La función _ensure_username() se elimina o se deja sin uso directo
    # ya que el username debe venir del constructor.

    def _save_game_state(self):
        """Guarda el estado actual del juego en un archivo JSON por usuario."""
        if not self.username: # MODIFICADO: Verificación directa de self.username
            self._show_message("No se puede guardar: Usuario no especificado.", 3000)
            print("Error: Intento de guardar partida sin nombre de usuario.")
            return

        username = self.username
        save_file_path = self.game_settings.SAVE_FILE_NAME # Ya es una ruta Path completa
        save_dir = self.game_settings.SAVES_DIR # Ya es una ruta Path completa
        
        os.makedirs(save_dir, exist_ok=True) # MODIFICADO: Asegurar que el directorio exista

        game_state = {
            'board': self.current_board,
            'target_words': self.palabras_objetivo,
            'found_words': list(self.found_words), 
            'score': self.score,
            'time_elapsed': self.time_elapsed,
            'current_selection_path': self.current_selection_path,
            'current_selected_word': self.current_selected_word
        }
        
        all_saves = {}
        if os.path.exists(save_file_path):
            try:
                with open(save_file_path, 'r', encoding='utf-8') as f:
                    all_saves = json.load(f)
            except json.JSONDecodeError: 
                print(f"Advertencia: El archivo {save_file_path} está corrupto o no es JSON válido. Se creará uno nuevo.")
                all_saves = {}
            except Exception as e: 
                print(f"Error al leer el archivo de guardado {save_file_path}: {e}. Se intentará sobrescribir.")
                all_saves = {}
        
        all_saves[username] = game_state
        
        try:
            with open(save_file_path, 'w', encoding='utf-8') as f:
                json.dump(all_saves, f, ensure_ascii=False, indent=4) 
            print(f"Partida guardada exitosamente para {username} en {save_file_path}")
            self._show_message("Partida guardada exitosamente.", 2000)
        except Exception as e:
            print(f"Error crítico al escribir en el archivo de guardado {save_file_path}: {e}")
            self._show_message(f"Error al guardar partida: {e}", 3000)


    def _load_game_action(self):
        """Carga el estado del juego desde un archivo JSON por usuario."""
        if not self.username: # MODIFICADO: Verificación directa de self.username
            self._show_message("No se puede cargar: Usuario no especificado.", 3000)
            print("Error: Intento de cargar partida sin nombre de usuario.")
            self._show_menu_interface() 
            return

        username = self.username
        save_file_path = self.game_settings.SAVE_FILE_NAME # Ya es una ruta Path completa

        if os.path.exists(save_file_path):
            try:
                with open(save_file_path, 'r', encoding='utf-8') as f:
                    all_saves = json.load(f)
                
                if username not in all_saves:
                    self._show_message(f"No hay partida guardada para '{username}'.", 2000)
                    print(f"No se encontró partida para el usuario '{username}'.")
                    return 
                
                game_state = all_saves[username]
                
                if not all(k in game_state for k in ['board', 'target_words', 'found_words', 'score', 'time_elapsed']):
                    raise ValueError("El estado del juego guardado está incompleto o corrupto.")

                self.current_board = game_state['board']
                self.palabras_objetivo = game_state['target_words']
                self.found_words = set(game_state['found_words']) 
                self.score = game_state['score']
                self.time_elapsed = game_state['time_elapsed']
                self.current_selection_path = game_state.get('current_selection_path', [])
                self.current_selected_word = game_state.get('current_selected_word', "")
                
                self._resume_loaded_game()
                self._show_message("Partida cargada exitosamente.", 2000)
                print(f"Partida cargada para {username} desde {save_file_path}")

            except json.JSONDecodeError:
                print(f"Error: El archivo de guardado '{save_file_path}' está corrupto o no es un JSON válido.")
                self._show_message("Error: Archivo de guardado corrupto.", 3000)
                self._show_menu_interface() 
            except ValueError as ve: 
                print(f"Error al cargar la partida: {ve}")
                self._show_message(f"Error al cargar: {ve}", 3000)
                self._show_menu_interface()
            except Exception as e: 
                print(f"Error desconocido al cargar la partida: {e}")
                self._show_message(f"Error al cargar partida: {e}", 3000)
                self._show_menu_interface()
        else:
            self._show_message(f"No hay archivo de partidas guardadas en {save_file_path}.", 2000) # MODIFICADO: Mostrar ruta
            print(f"No se encontró archivo de partidas guardadas: {save_file_path}")


    def _resume_loaded_game(self):
        """Reanuda el juego con el estado cargado."""
        self.game_active = True
        self.timer_running = True 
        
        if not self.current_board: 
            self._show_message("Error: Tablero no disponible al cargar.", 3000)
            self._back_to_menu_action() 
            return

        self.game_ui.display_board(self.current_board, self.current_selection_path) 
        self.game_ui.set_entry_text(self.current_selected_word) 

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
        if not self.username: # MODIFICADO: Verificación directa
            self._show_message("Error: Usuario no definido para iniciar nueva partida.", 3000)
            self.menu_ui.enable_start_button()
            return

        self.menu_ui.disable_start_button()
        self._show_message("Cargando palabras y generando tablero...", 0) 
        self.root.update() 

        # Asegurarse de que WORD_FILE en game_settings sea una cadena para WordGenerator
        self.word_generator.game_settings.WORD_FILE = str(self.game_settings.WORD_FILE)
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

        pos = (row, col)
        if self.current_selection_path and self.current_selection_path[-1] == pos:
            self.current_selection_path.pop()
            self.current_selected_word = self.current_selected_word[:-1]
        elif pos not in self.current_selection_path: 
            is_valid_next_step = False
            if not self.current_selection_path: 
                is_valid_next_step = True
            else:
                last_r, last_c = self.current_selection_path[-1]
                adjacents = self.word_generator._get_adjacent_cells(last_r, last_c, 
                                                                    self.game_settings.GRID_SIZE[0], 
                                                                    self.game_settings.GRID_SIZE[1])
                if pos in adjacents:
                    is_valid_next_step = True
            
            if is_valid_next_step:
                self.current_selection_path.append(pos)
                self.current_selected_word += letter

        self.game_ui.update_board_selection(self.current_selection_path)
        self.game_ui.set_entry_text(self.current_selected_word)


    def _reset_grid_selection(self):
        """Reinicia la selección visual de la grilla y el campo de entrada."""
        self.current_selection_path.clear()
        self.current_selected_word = ""
        if self.game_ui: 
            self.game_ui.update_board_selection(self.current_selection_path)
            self.game_ui.clear_entry()

    def check_word(self):
        """Verifica si la palabra ingresada/seleccionada es correcta."""
        if not self.game_active or not self.timer_running: return
        
        word_input = self.game_ui.get_entered_word().strip().upper() 

        if not word_input: 
            self._reset_grid_selection()
            return

        if word_input in self.palabras_objetivo and word_input not in self.found_words:
            self._word_found(word_input)
        elif word_input in self.found_words:
            self._show_message(f"'{word_input}' ya fue encontrada.", 2000)
            self.sound_manager.play_incorrect_sound()
        else:
            self._show_message(f"'{word_input}' no es una palabra objetivo.", 2000)
            self.sound_manager.play_incorrect_sound()
        
        self._reset_grid_selection() 


    def _word_found(self, word: str):
        """Actualiza el estado del juego cuando se encuentra una palabra."""
        self.found_words.add(word)
        self.game_ui.update_found_word_display(word) 

        base_score = len(word) * 100 
        time_bonus = max(0, 300 - (self.time_elapsed // (len(self.palabras_objetivo) if self.palabras_objetivo else 1))) 
        word_score = base_score + time_bonus
        self.score += word_score

        self.game_ui.update_status_labels(len(self.found_words), len(self.palabras_objetivo), self.score)
        self.sound_manager.play_correct_sound()
        self._show_message(f"¡'{word}' encontrada! +{word_score} puntos", 2500)

        if len(self.found_words) == len(self.palabras_objetivo):
            self._end_game(from_back_to_menu=False) 


    def _show_message(self, message: str, duration: int = 2000):
        """Muestra un mensaje temporal en la interfaz."""
        if hasattr(self.game_ui, 'show_message') and hasattr(self.game_ui, 'clear_message'):
            self.game_ui.show_message(message)
            if self._message_after_id is not None:
                self.root.after_cancel(self._message_after_id)
                self._message_after_id = None 
            if duration > 0: 
                self._message_after_id = self.root.after(duration, self.game_ui.clear_message)
        else:
            print(f"Mensaje UI (no mostrado en GUI): {message}")


    def _update_timer(self):
        """Actualiza el temporizador del juego."""
        if self.timer_running and self.game_active:
            self.time_elapsed += 1
            if hasattr(self.game_ui, 'update_timer_label'): 
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
        
        if hasattr(self.game_ui, 'disable_game_controls'): 
            self.game_ui.disable_game_controls()
        self._show_message("Juego Pausado", 0) 


    def _resume_game(self):
        """Reanuda el juego y sus elementos."""
        self.timer_running = True
        if hasattr(self.game_ui, 'enable_game_controls'): 
            self.game_ui.enable_game_controls()
        
        if hasattr(self.game_ui, 'update_timer_label'):
             self.game_ui.update_timer_label(self._format_time(self.time_elapsed)) 
        
        if self._timer_after_id is None:
            self._timer_after_id = self.root.after(1000, self._update_timer)
        
        self._show_message("Juego Reanudado", 2000)


    def toggle_music(self):
        """Alterna la reproducción de la música de fondo."""
        self.sound_manager.toggle_music()
        music_status_text = self.sound_manager.get_music_status_text()
        if hasattr(self.menu_ui, 'update_music_button_text'):
            self.menu_ui.update_music_button_text(music_status_text)
        if hasattr(self.game_ui, 'update_music_button_text'):
            self.game_ui.update_music_button_text(music_status_text)


    def clear_entry_input(self):
        """Limpia el texto introducido manualmente en el campo de entrada."""
        if hasattr(self.game_ui, 'clear_entry'): 
            self.game_ui.clear_entry()


    def _end_game(self, from_back_to_menu: bool = False):
        """Finaliza el juego, detiene el temporizador y muestra el resumen o vuelve al menú."""
        self.game_active = False
        self.timer_running = False 
        
        if self._timer_after_id is not None: 
            self.root.after_cancel(self._timer_after_id)
            self._timer_after_id = None

        self.clear_entry_input() 

        if hasattr(self.game_ui, 'disable_game_controls'):
            self.game_ui.disable_game_controls() 

        if not from_back_to_menu: 
            self.sound_manager.play_winning_sound()
            final_message = f"¡Juego Completado!\nUsuario: {self.username}\nPuntuación Final: {self.score}\nTiempo Total: {self._format_time(self.time_elapsed)}"
            self._show_message(final_message, 0) 
            self.root.after(7000, self._show_menu_interface) 
        else: 
            if hasattr(self.game_ui, 'clear_message'):
                self.game_ui.clear_message() 


    def _on_clear_button_click(self):
        """Maneja el evento de clic en el botón 'Limpiar'."""
        if not self.game_active or not self.timer_running: return
        self._reset_grid_selection()


    def _create_how_to_play_window(self, title: str):
        """Crea y muestra la ventana de "Cómo Jugar"."""
        how_to_play_window = tk.Toplevel(self.root)
        how_to_play_window.title(title)
        how_to_play_window.resizable(False, False)
        how_to_play_window.config(bg=self.ui_settings.COLORS['bg'])
        how_to_play_window.attributes("-topmost", True) 

        self.root.update_idletasks() 
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()

        win_width = 450 
        win_height = 400 

        x = main_x + (main_width // 2) - (win_width // 2)
        y = main_y + (main_height // 2) - (win_height // 2)
        how_to_play_window.geometry(f'{win_width}x{win_height}+{x}+{y}')

        font_ui_tuple = (self.ui_settings.MAIN_FONT_FAMILY, self.ui_settings.UI_FONT_SIZE -1) 
        font_ui_bold_tuple = (self.ui_settings.MAIN_FONT_FAMILY, self.ui_settings.UI_FONT_SIZE, "bold")

        how_to_play_text = f"""
¡Bienvenido a Lexigrama, {self.username if self.username else "Jugador"}!

Tu objetivo es encontrar las {self.game_settings.TARGET_WORDS_COUNT} palabras ocultas.

Instrucciones:
1.  Forma palabras seleccionando letras adyacentes en el tablero (horizontal, vertical). No se permiten diagonales.
2.  Haz clic en una letra para iniciar tu palabra. Sigue haciendo clic en letras adyacentes.
3.  Para anular la última letra seleccionada, haz clic en ella nuevamente.
4.  Para borrar toda tu selección actual, usa el botón "Limpiar".
5.  Una vez que hayas formado una palabra, presiona "Enviar" o la tecla Enter.
6.  Cada celda solo puede usarse una vez por palabra.

Puntuación:
-   Se otorgan puntos por cada palabra correcta.
-   ¡Las palabras más largas y encontradas rápidamente dan más puntos!

¡Mucha suerte y diviértete!
        """

        text_frame = tk.Frame(how_to_play_window, bg=self.ui_settings.COLORS['bg'], bd=2, relief=tk.GROOVE)
        text_frame.pack(padx=15, pady=15, expand=True, fill="both")
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, 
                              font=font_ui_tuple, 
                              bg=self.ui_settings.COLORS['bg'], 
                              fg=self.ui_settings.COLORS['fg'],
                              padx=10, pady=10, bd=0, highlightthickness=0)
        text_widget.insert(tk.END, how_to_play_text)
        text_widget.config(state=tk.DISABLED) 
        text_widget.pack(expand=True, fill="both")


        close_button = tk.Button(
            how_to_play_window,
            text="Entendido",
            command=how_to_play_window.destroy,
            font=font_ui_bold_tuple, 
            bg=self.ui_settings.COLORS['button_bg'], 
            fg=self.ui_settings.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2, width=12, height=1, padx=5, pady=5
        )
        close_button.pack(pady=(0, 15)) 

        how_to_play_window.transient(self.root) 
        how_to_play_window.grab_set() 
        self.root.wait_window(how_to_play_window)


    def run(self):
        """Inicia el bucle principal de la aplicación Tkinter."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nJuego cerrado por el usuario.")
        finally:
            if pygame.get_init(): 
                pygame.quit() 
            print("Aplicación Lexigrama finalizada.")
