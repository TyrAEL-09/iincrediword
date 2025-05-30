import tkinter as tk
from typing import List, Tuple, Set, Dict, Callable, Optional

class BoggleUI:
    def __init__(self, root: tk.Tk, colors: Dict[str, str], grid_size: Tuple[int, int], 
                 iniciar_juego_callback: Callable, 
                 check_word_callback: Callable, 
                 toggle_pause_callback: Callable, 
                 toggle_music_callback: Callable):
        self.root = root
        self.colors = colors
        self.grid_size = grid_size # Potentially useful for frame sizing, though not directly used for cell creation here

        self.iniciar_juego_callback = iniciar_juego_callback
        self.check_word_callback = check_word_callback
        self.toggle_pause_callback = toggle_pause_callback
        self.toggle_music_callback = toggle_music_callback
        
        self.hint_labels: Dict[str, tk.Label] = {} # Stores labels for words to find

        self._setup_frames()
        self._create_main_widgets()
        self._create_input_widgets()
        # self._create_sound_buttons() # Combined into _create_input_widgets for now

    def _setup_frames(self):
        """Crea los marcos principales para la UI."""
        self.root.configure(bg=self.colors['bg'])
        self.root.grid_rowconfigure(0, weight=1) # For sopa
        self.root.grid_rowconfigure(1, weight=0) # For input area
        self.root.grid_rowconfigure(2, weight=0) # For start button
        self.root.grid_columnconfigure(0, weight=1) # For sopa and input
        self.root.grid_columnconfigure(1, weight=0) # For lista palabras

        self.frame_sopa = tk.Frame(self.root, bg=self.colors['bg'])
        self.frame_sopa.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        
        self.frame_input = tk.Frame(self.root, bg=self.colors['bg'])
        # frame_input is gridded later by mostrar_interfaz_juego
        
        self.frame_lista = tk.Frame(self.root, bg=self.colors['bg'])
        self.frame_lista.grid(row=0, column=1, rowspan=3, sticky='ns', padx=20, pady=20)

    def _create_main_widgets(self):
        """Crea el botón de iniciar juego."""
        self.boton_iniciar = tk.Button(
            self.root, text="Iniciar Juego", command=self.iniciar_juego_callback,
            bg=self.colors['button_bg'], fg=self.colors['button_fg'], 
            font=("Arial", 12)
        )
        self.boton_iniciar.grid(row=2, column=0, columnspan=2, pady=10)

    def _create_input_widgets(self):
        """Crea los widgets para la entrada de palabras, estado y controles."""
        # Status Label (palabras encontradas, puntuación)
        self.label_status = tk.Label(
            self.frame_input, text="Palabras: 0/0 | Puntuación: 0",
            font=("Arial", 12), bg=self.colors['bg'], fg=self.colors['fg']
        )
        self.label_status.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,5))
        
        # Timer Label
        self.label_timer = tk.Label(
            self.frame_input, text="Tiempo: 0s", 
            font=("Arial", 12), bg=self.colors['bg'], fg=self.colors['fg']
        )
        self.label_timer.grid(row=0, column=2, padx=5, sticky="e", pady=(0,5))
        
        # Word Entry
        self.entry = tk.Entry(
            self.frame_input, font=("Arial", 12), 
            bg=self.colors['grid'], fg=self.colors['fg'], 
            insertbackground=self.colors['fg'], width=30 # Increased width
        )
        self.entry.grid(row=1, column=0, padx=(0,5), sticky="ew")
        self.entry.bind('<Return>', lambda event: self.check_word_callback())
        
        # Submit Button
        self.button_submit = tk.Button(
            self.frame_input, text="Enviar", command=self.check_word_callback,
            font=("Arial", 12), bg=self.colors['button_bg'], fg=self.colors['button_fg']
        )
        self.button_submit.grid(row=1, column=1, padx=(0,5))
        
        # Pause/Resume Button
        self.button_pause = tk.Button(
            self.frame_input, text="Pausar", command=self.toggle_pause_callback,
            font=("Arial", 12), bg=self.colors['button_bg'], fg=self.colors['button_fg']
        )
        # Gridded by _show_game_interface
        
        # Message Label (for "Palabra encontrada", "Inválida", etc.)
        self.label_message = tk.Label(
            self.frame_input, text="", font=("Arial", 10, "italic"), 
            bg=self.colors['bg'], fg=self.colors['fg'], height=2 # Reserve space
        )
        self.label_message.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(5,0))
        
        # Music Toggle Button
        self.button_music = tk.Button(
            self.frame_input, text="Pausar Música", command=self.toggle_music_callback,
            font=("Arial", 12), bg=self.colors['button_bg'], fg=self.colors['button_fg']
        )
        # Gridded by _show_game_interface

        self.frame_input.grid_columnconfigure(0, weight=1) # Allow entry to expand

    def mostrar_tablero(self, tablero_data: List[List[str]]):
        """Muestra el tablero (sopa de letras) en la UI."""
        for widget in self.frame_sopa.winfo_children():
            widget.destroy()
            
        for i, fila in enumerate(tablero_data):
            for j, letra in enumerate(fila):
                label = tk.Label(
                    self.frame_sopa, text=letra, font=("Arial", 20, "bold"), # Bolder font
                    width=3, height=2, borderwidth=2, relief="raised", # More 3D effect
                    bg=self.colors.get('grid_cell_bg', self.colors['grid']), # Allow custom cell bg
                    fg=self.colors.get('grid_cell_fg', self.colors['fg'])
                )
                label.grid(row=i, column=j, padx=1, pady=1) # Add small padding

    def mostrar_lista_palabras(self, palabras_por_longitud: Dict[int, List[str]], found_words: Set[str]):
        """Muestra la lista de palabras a encontrar, marcando las ya encontradas."""
        for widget in self.frame_lista.winfo_children():
            widget.destroy()
        
        titulo = tk.Label(
            self.frame_lista, text="Palabras a encontrar:", 
            font=("Arial", 14, "bold"), bg=self.colors['bg'], fg=self.colors['fg']
        )
        titulo.pack(pady=(0, 10), anchor="w")
        
        self.hint_labels.clear()
        
        for longitud in sorted(palabras_por_longitud.keys(), reverse=True):
            subtitulo = tk.Label(
                self.frame_lista, text=f"{longitud} letras:", 
                font=("Arial", 12, "italic"), bg=self.colors['bg'], fg="#cccccc" # Lighter fg for subtitle
            )
            subtitulo.pack(pady=(8, 3), anchor="w")
            
            for palabra in sorted(palabras_por_longitud[longitud]):
                display_text = palabra if palabra in found_words else palabra[0] + ' _' * (len(palabra) - 1)
                fg_color = "#90EE90" if palabra in found_words else self.colors['fg']
                
                label = tk.Label(
                    self.frame_lista, text=display_text, font=("Arial", 11), # Slightly smaller font
                    bg=self.colors['bg'], fg=fg_color
                )
                label.pack(pady=1, anchor="w")
                self.hint_labels[palabra.upper()] = label # Store with uppercase key
        return self.hint_labels # Return for BoggleGame to store if needed

    def actualizar_estado(self, encontradas: int, total_palabras: int, puntuacion: int):
        """Actualiza el label de estado (palabras encontradas, puntuación)."""
        self.label_status.config(
            text=f"Palabras: {encontradas}/{total_palabras} | Puntuación: {puntuacion}"
        )

    def actualizar_timer(self, tiempo_str: str):
        """Actualiza el label del temporizador."""
        self.label_timer.config(text=f"Tiempo: {tiempo_str}")

    def mostrar_mensaje(self, mensaje: str, duration: int = 2000, error: bool = False):
        """Muestra un mensaje temporal en el label de mensajes."""
        original_fg = self.colors['fg']
        if error:
            self.label_message.config(text=mensaje, fg="red")
        else:
            self.label_message.config(text=mensaje, fg=original_fg) # Use default for non-errors
        
        if hasattr(self, "_mensaje_after_id"): # Cancel previous auto-clear if any
            self.root.after_cancel(self._mensaje_after_id)
            
        self._mensaje_after_id = self.root.after(duration, lambda: self.label_message.config(text="", fg=original_fg))

    def revelar_palabra_encontrada(self, palabra: str):
        """Actualiza el label de una palabra encontrada en la lista."""
        palabra_upper = palabra.upper()
        if palabra_upper in self.hint_labels:
            self.hint_labels[palabra_upper].config(text=palabra_upper, fg="#90EE90") # Verde claro

    def configurar_estado_juego_activo(self, activo: bool):
        """Habilita o deshabilita los controles de entrada según el estado del juego."""
        estado_tk = tk.NORMAL if activo else tk.DISABLED
        self.entry.config(state=estado_tk)
        self.button_submit.config(state=estado_tk)

    def configurar_estado_pausa(self, pausado: bool):
        """Actualiza el texto del botón de pausa y el estado de los controles."""
        if pausado:
            self.button_pause.config(text="Reanudar")
            self.configurar_estado_juego_activo(False) # Disable entry/submit when paused
        else:
            self.button_pause.config(text="Pausar")
            self.configurar_estado_juego_activo(True) # Enable entry/submit when resumed

    def mostrar_interfaz_juego(self, mostrar_input: bool):
        """Muestra u oculta elementos de la UI para el estado de juego activo."""
        if mostrar_input:
            self.boton_iniciar.grid_forget()
            self.frame_input.grid(row=1, column=0, sticky='ew', padx=20, pady=(10,0)) # Adjusted pady
            self.button_pause.grid(row=3, column=0, columnspan=1, pady=5, padx=(0,5), sticky="w") # place pause
            self.button_music.grid(row=3, column=1, columnspan=2, pady=5, padx=(5,0), sticky="e") # place music
        else: # Typically when game ends or before start
            self.frame_input.grid_forget()
            self.boton_iniciar.grid(row=2, column=0, columnspan=2, pady=10) # Show start button again
            
    def get_entry_value(self) -> str:
        """Obtiene el valor del campo de entrada y lo limpia."""
        word = self.entry.get()
        self.entry.delete(0, tk.END)
        return word
        
    def set_music_button_text(self, text: str):
        """Actualiza el texto del botón de música."""
        self.button_music.config(text=text)

```
