# game_ui.py
import tkinter as tk
from tkinter import PhotoImage, Frame, Label, Button, Entry, SOLID, RAISED, DISABLED, NORMAL, END
from typing import List, Tuple, Optional, Dict, Set
from PIL import Image, ImageTk
from config.settings import UI_SETTINGS # Asegúrate de importar UI_SETTINGS

class GameUI:
    """Gestiona la creación y actualización de la interfaz de usuario del juego."""

    def __init__(self, root: tk.Tk, ui_settings, on_cell_click, on_submit_word, on_pause_toggle, on_music_toggle, on_clear_selection, on_how_to_play_game_click, on_back_to_menu_and_save):
        self.root = root
        self.ui_settings = ui_settings
        self.on_cell_click_callback = on_cell_click
        self.on_submit_word_callback = on_submit_word
        self.on_pause_toggle_callback = on_pause_toggle
        self.on_music_toggle_callback = on_music_toggle
        self.on_clear_selection_callback = on_clear_selection
        self.on_how_to_play_game_click = on_how_to_play_game_click
        self.on_back_to_menu_and_save_callback = on_back_to_menu_and_save

        self.grid_cell_widgets: List[List[Optional[tk.Button]]] = []
        self.hint_labels: Dict[str, List[tk.Label]] = {}

        self.frame_sopa = tk.Frame(root, bg=self.ui_settings.COLORS['bg'])
        self.frame_input = tk.Frame(root, bg=self.ui_settings.COLORS['bg'])
        self.frame_lista = tk.Frame(root, bg=self.ui_settings.COLORS['bg'])

        # Atributo para almacenar el estado de la música
        self.music_on = False # Inicialmente asumimos que la música está apagada

        self._create_game_widgets()

    def _on_button_enter(self, event):
        """Cambia el color de fondo del botón cuando el cursor entra."""
        event.widget.config(
            bg=self.ui_settings.COLORS.get('button_hover_bg', self.ui_settings.COLORS['button_bg']),
            fg=self.ui_settings.COLORS.get('button_hover_fg', self.ui_settings.COLORS['button_fg'])
        )

    def _on_button_leave(self, event):
        """Restaura el color de fondo del botón cuando el cursor sale."""
        event.widget.config(
            bg=self.ui_settings.COLORS['button_bg'],
            fg=self.ui_settings.COLORS['button_fg']
        )

    def _create_game_widgets(self):
        """Crea los widgets principales de la interfaz de juego."""
        font_ui_tuple = (self.ui_settings.MAIN_FONT_FAMILY, self.ui_settings.UI_FONT_SIZE)
        font_ui_bold_tuple = (self.ui_settings.MAIN_FONT_FAMILY, self.ui_settings.UI_FONT_SIZE, "bold")
        
        font_special_button = (self.ui_settings.MAIN_FONT_FAMILY, self.ui_settings.UI_FONT_SIZE, "bold")

        self.label_status = tk.Label(
            self.frame_input, text="Palabras: 0/0 | Puntuación: 0",
            font=font_ui_tuple, bg=self.ui_settings.COLORS['bg'], fg=self.ui_settings.COLORS['fg']
        )
        self.label_status.grid(row=0, column=0, columnspan=2, pady=(0,5), sticky="w")

        self.label_timer = tk.Label(
            self.frame_input, text="Tiempo: 00:00",
            font=font_ui_tuple, bg=self.ui_settings.COLORS['bg'], fg=self.ui_settings.COLORS['fg']
        )
        self.label_timer.grid(row=0, column=2, padx=5, pady=(0,5), sticky="e")

        self.entry = tk.Entry(
            self.frame_input, font=font_ui_tuple,
            bg=self.ui_settings.COLORS['grid'], fg=self.ui_settings.COLORS['fg'],
            insertbackground=self.ui_settings.COLORS['fg'], relief=tk.SOLID, borderwidth=1
        )
        self.entry.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        self.entry.bind('<Return>', lambda e: self.on_submit_word_callback())
        self.entry.bind('<KeyRelease>', self._capitalize_entry_text)

        self.button_submit = tk.Button(
            self.frame_input, text="Enviar", command=self.on_submit_word_callback,
            font=font_ui_bold_tuple, bg=self.ui_settings.COLORS['button_bg'], fg=self.ui_settings.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2
        )
        self.button_submit.grid(row=2, column=0, columnspan=2, padx=(5,2), pady=5, sticky="ew")
        self.button_submit.bind("<Enter>", self._on_button_enter)
        self.button_submit.bind("<Leave>", self._on_button_leave)

        self.button_clear = tk.Button(
            self.frame_input, text="Limpiar", command=self.on_clear_selection_callback,
            font=font_ui_bold_tuple, bg=self.ui_settings.COLORS['button_bg'], fg=self.ui_settings.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2
        )
        self.button_clear.grid(row=2, column=2, padx=(2,5), pady=5, sticky="ew")
        self.button_clear.bind("<Enter>", self._on_button_enter)
        self.button_clear.bind("<Leave>", self._on_button_leave)

        self.button_pause_game = tk.Button(
            self.frame_input, text="Pausar", command=self.on_pause_toggle_callback,
            font=font_ui_bold_tuple, bg=self.ui_settings.COLORS['button_bg'], fg=self.ui_settings.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2
        )
        self.button_pause_game.grid(row=3, column=0, columnspan=1, pady=5, sticky="ew", padx=(5,2))
        self.button_pause_game.bind("<Enter>", self._on_button_enter)
        self.button_pause_game.bind("<Leave>", self._on_button_leave)

        # Modificación del botón de música
        self.button_music_game = tk.Button(
            self.frame_input, text="♬", 
            command=self.on_music_toggle_callback,
            font=font_special_button, # Usar la fuente común para botones especiales
            bg=self.ui_settings.COLORS['button_bg'], fg=self.ui_settings.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2,
            width=2, height=1 # Establecer un ancho y alto explícito para hacerlo cuadrado
        )
        self.button_music_game.grid(row=3, column=1, columnspan=2, pady=5, sticky="ew", padx=(2,5))
        self.button_music_game.bind("<Enter>", self._on_button_enter)
        self.button_music_game.bind("<Leave>", self._on_button_leave)

        # Crear un frame para los botones de la esquina inferior derecha
        self.frame_bottom_right_buttons = tk.Frame(self.frame_input, bg=self.ui_settings.COLORS['bg'])
        self.frame_bottom_right_buttons.grid(row=4, column=0, columnspan=3, pady=5, sticky="se")

        # Botón "Cómo Jugar" dentro del nuevo frame, cuadrado y con "?"
        self.button_how_to_play_game = tk.Button(
            self.frame_bottom_right_buttons, text="?", command=self.on_how_to_play_game_click,
            font=font_special_button, # Usar la fuente común para botones especiales
            bg=self.ui_settings.COLORS['button_bg'], fg=self.ui_settings.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2,
            width=2, height=1 # Establecer un ancho y alto explícito para hacerlo cuadrado
        )
        self.button_how_to_play_game.pack(side=tk.LEFT, padx=(5,2))
        self.button_how_to_play_game.bind("<Enter>", self._on_button_enter)
        self.button_how_to_play_game.bind("<Leave>", self._on_button_leave)

        # Botón "Volver al Menú" dentro del nuevo frame
        self.button_back_to_menu = tk.Button(
            self.frame_bottom_right_buttons, text="Volver al Menú", command=self.on_back_to_menu_and_save_callback,
            font=font_ui_bold_tuple, bg=self.ui_settings.COLORS['button_bg'], fg=self.ui_settings.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2
        )
        self.button_back_to_menu.pack(side=tk.LEFT, padx=(2,5), fill="x", expand=True)
        self.button_back_to_menu.bind("<Enter>", self._on_button_enter)
        self.button_back_to_menu.bind("<Leave>", self._on_button_leave)

        self.label_message = tk.Label(
            self.frame_input, text="", font=font_ui_tuple,
            bg=self.ui_settings.COLORS['bg'], fg=self.ui_settings.COLORS['fg'], wraplength=350
        )
        self.label_message.grid(row=5, column=0, columnspan=3, pady=5, sticky="ew")

        self.frame_input.grid_columnconfigure(0, weight=1)
        self.frame_input.grid_columnconfigure(1, weight=1)
        self.frame_input.grid_columnconfigure(2, weight=1)

        self.frame_bottom_right_buttons.grid_columnconfigure(0, weight=1)
        
        # Llama a update_music_button_text al inicio para establecer el estado inicial correcto del icono
        self.update_music_button_text(self.music_on)

    def _capitalize_entry_text(self, event):
        current_text = self.entry.get()
        capitalized_text = current_text.upper()
        if current_text != capitalized_text:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, capitalized_text)

    def show_game_interface(self):
        """Muestra los frames de la interfaz de juego y oculta otros.
        Establece el tamaño de la ventana a una dimensión más pequeña y cuadrada."""
        desired_width = 750
        desired_height = 750

        self.root.geometry(f"{desired_width}x{desired_height}")

        self.frame_sopa.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.frame_lista.grid(row=0, column=1, rowspan=2, sticky='ns', padx=10, pady=10)
        self.frame_input.grid(row=1, column=0, sticky='ew', padx=10, pady=(5,10))

        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=3)
        self.root.grid_rowconfigure(1, weight=1)

        self.entry.config(state=NORMAL)
        self.button_submit.config(state=NORMAL)
        self.button_clear.config(state=NORMAL)
        self.button_pause_game.config(state=NORMAL, text="Pausar")
        self.button_back_to_menu.config(state=NORMAL)
        self.entry.focus_set()

    def hide_game_interface(self):
        """Oculta los frames de la interfaz de juego."""
        self.frame_sopa.grid_remove()
        self.frame_input.grid_remove()
        self.frame_lista.grid_remove()

    def display_board(self, board: List[List[str]], current_selection_path: List[Tuple[int, int]]):
        """Dibuja o actualiza el tablero de letras."""
        for widget in self.frame_sopa.winfo_children():
            widget.destroy()
        self.grid_cell_widgets = [[None for _ in range(len(board[0]))] for _ in range(len(board))]
        font_grid_tuple = (self.ui_settings.MAIN_FONT_FAMILY, self.ui_settings.GRID_LETTER_FONT_SIZE, "bold")

        for r_idx, row_letters in enumerate(board):
            self.frame_sopa.grid_rowconfigure(r_idx, weight=1)
            for c_idx, letter in enumerate(row_letters):
                self.frame_sopa.grid_columnconfigure(c_idx, weight=1)
                cell_bg = self.ui_settings.COLORS['selected_cell_bg'] if (r_idx, c_idx) in current_selection_path else self.ui_settings.COLORS['grid']
                cell_button = tk.Button(
                    self.frame_sopa, text=letter,
                    font=font_grid_tuple,
                    borderwidth=1, relief=tk.SOLID,
                    bg=cell_bg,
                    fg=self.ui_settings.COLORS['grid_fg'],
                    activebackground=self.ui_settings.COLORS['selected_cell_bg'],
                    activeforeground=self.ui_settings.COLORS['grid_fg'],
                    command=lambda r=r_idx, c=c_idx, l=letter: self.on_cell_click_callback(r, c, l)
                )
                cell_button.grid(row=r_idx, column=c_idx, padx=1, pady=1, sticky="nsew")
                self.grid_cell_widgets[r_idx][c_idx] = cell_button

    def update_board_selection(self, current_selection_path: List[Tuple[int, int]]):
        """Actualiza visualmente la selección de celdas en el tablero."""
        for r_idx in range(len(self.grid_cell_widgets)):
            for c_idx in range(len(self.grid_cell_widgets[0])):
                if self.grid_cell_widgets[r_idx][c_idx]:
                    self.grid_cell_widgets[r_idx][c_idx].config(bg=self.ui_settings.COLORS['grid'])
        for r_idx, c_idx in current_selection_path:
            if 0 <= r_idx < len(self.grid_cell_widgets) and 0 <= c_idx < len(self.grid_cell_widgets[0]):
                if self.grid_cell_widgets[r_idx][c_idx]:
                    self.grid_cell_widgets[r_idx][c_idx].config(bg=self.ui_settings.COLORS['selected_cell_bg'])

    def display_word_list(self, words_by_length: Dict[int, List[str]], found_words: Set[str]):
        """Dibuja o actualiza la lista de palabras a encontrar."""
        for widget in self.frame_lista.winfo_children():
            widget.destroy()
        font_ui_tuple = (self.ui_settings.MAIN_FONT_FAMILY, self.ui_settings.UI_FONT_SIZE)
        font_ui_bold_tuple = (self.ui_settings.MAIN_FONT_FAMILY, self.ui_settings.UI_FONT_SIZE, "bold")
        font_hint_box_tuple = (self.ui_settings.MAIN_FONT_FAMILY, self.ui_settings.UI_FONT_SIZE - 1, "bold")

        titulo = tk.Label(self.frame_lista, text="Palabras:", font=font_ui_bold_tuple, bg=self.ui_settings.COLORS['bg'], fg=self.ui_settings.COLORS['fg'])
        titulo.pack(pady=(0, 10), anchor="w")
        self.hint_labels.clear()

        if not words_by_length:
            info_label = tk.Label(self.frame_lista, text="No hay palabras...", font=font_ui_tuple, bg=self.ui_settings.COLORS['bg'], fg=self.ui_settings.COLORS['hint_fg'])
            info_label.pack(anchor="w")
            return

        for length in sorted(words_by_length.keys(), reverse=True):
            subtitulo_text = f"{length} letras:"
            subtitulo = tk.Label(self.frame_lista, text=subtitulo_text, font=font_ui_tuple, bg=self.ui_settings.COLORS['bg'], fg=self.ui_settings.COLORS['hint_fg'] )
            subtitulo.pack(pady=(8, 3), anchor="w")
            for word_str in sorted(words_by_length[length]):
                word_hint_container = tk.Frame(self.frame_lista, bg=self.ui_settings.COLORS['bg'])
                word_hint_container.pack(pady=2, padx=5, anchor="w")
                letter_box_labels_for_word = []
                is_found = word_str.upper() in found_words
                for idx, char_in_palabra in enumerate(word_str):
                    box_text = char_in_palabra.upper() if is_found else ""
                    if not is_found and idx == 0:
                        box_text = word_str[0].upper()

                    box_fg = self.ui_settings.COLORS['found_word_fg'] if is_found else self.ui_settings.COLORS['hint_box_fg']

                    letter_box_label = tk.Label(
                        word_hint_container, text=box_text, font=font_hint_box_tuple,
                        bg=self.ui_settings.COLORS['hint_box_bg'], fg=box_fg,
                        borderwidth=1, relief=tk.SOLID, width=2, height=1, anchor='center'
                    )
                    letter_box_label.pack(side=tk.LEFT, padx=1)
                    letter_box_labels_for_word.append(letter_box_label)
                self.hint_labels[word_str.upper()] = letter_box_labels_for_word

    def update_found_word_display(self, word: str):
        """Actualiza la visualización de una palabra encontrada en la lista de pistas."""
        word_upper = word.upper()
        if word_upper in self.hint_labels:
            letter_boxes = self.hint_labels[word_upper]
            for i, box_label in enumerate(letter_boxes):
                if i < len(word):
                    box_label.config(text=word[i].upper(), fg=self.ui_settings.COLORS['found_word_fg'])

    def update_status_labels(self, found_count: int, target_count: int, score: int):
        """Actualiza las etiquetas de estado del juego."""
        status_text = f"Palabras: {found_count}/{target_count} | Puntos: {score}"
        self.label_status.config(text=status_text)

    def update_timer_label(self, formatted_time: str):
        """Actualiza la etiqueta del temporizador."""
        self.label_timer.config(text=f"Tiempo: {formatted_time}")

    def show_message(self, message: str):
        """Muestra un mensaje temporal en la interfaz."""
        self.label_message.config(text=message)

    def clear_message(self):
        """Borra el mensaje temporal."""
        self.label_message.config(text="")

    def get_entered_word(self) -> str:
        """Obtiene el texto del campo de entrada."""
        return self.entry.get().strip().upper()

    def clear_entry(self):
        """Borra el contenido del campo de entrada."""
        self.entry.delete(0, END)

    def set_entry_text(self, text: str):
        """Establece el texto del campo de entrada."""
        self.entry.delete(0, END)
        self.entry.insert(0, text)

    def update_music_button_text(self, music_is_on: bool):
        """Actualiza el texto del botón de música en la interfaz de juego
        para mostrar una clave de sol o una clave de sol tachada."""
        self.music_on = music_is_on # Actualiza el estado interno
        if self.music_on:
            self.button_music_game.config(text="♬") # Clave de sol
        else:
            self.button_music_game.config(text="♬̷") # Clave de sol tachada (combinando U+266C con U+0338)

    def enable_game_controls(self):
        """Habilita los controles del juego (entrada, botones, tablero)."""
        self.entry.config(state=NORMAL)
        self.button_submit.config(state=NORMAL)
        self.button_clear.config(state=NORMAL)
        self.button_pause_game.config(state=NORMAL, text="Pausar")
        self.button_back_to_menu.config(state=NORMAL)
        self.button_music_game.config(state=NORMAL) # Asegúrate de habilitar el botón de música
        if self.grid_cell_widgets:
            for row_widgets in self.grid_cell_widgets:
                for widget_cell in row_widgets:
                    if widget_cell: widget_cell.config(state=NORMAL)
        self.entry.focus_set()

    def disable_game_controls(self):
        """Deshabilita los controles del juego (entrada, botones, tablero)."""
        self.entry.config(state=DISABLED)
        self.button_submit.config(state=DISABLED)
        self.button_clear.config(state=DISABLED)
        self.button_pause_game.config(text="Reanudar")
        self.button_back_to_menu.config(state=DISABLED)
        self.button_music_game.config(state=DISABLED) # Asegúrate de deshabilitar el botón de música
        if self.grid_cell_widgets:
            for row_widgets in self.grid_cell_widgets:
                for widget_cell in row_widgets:
                    if widget_cell: widget_cell.config(state=DISABLED)