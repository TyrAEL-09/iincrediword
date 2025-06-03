# ui/menu_ui.py
import tkinter as tk
from PIL import Image, ImageTk
import os

class MenuUI:
    """Gestiona la creación y actualización de la interfaz de usuario del menú principal."""

    def __init__(self, root: tk.Tk, ui_settings, on_start_game, on_music_toggle, on_back_menu, on_how_to_play_menu_click, on_load_game):
        self.root = root
        self.ui_settings = ui_settings
        self.on_start_game_callback = on_start_game # Ahora será para "Nueva Partida"
        self.on_music_toggle_callback = on_music_toggle
        self.on_back_menu_callback = on_back_menu # Este callback es genérico para volver al menú
        self.on_how_to_play_menu_click = on_how_to_play_menu_click
        self.on_load_game_callback = on_load_game # Nuevo callback para cargar partida

        self.logo_tk_image = None
        self.frame_menu = tk.Frame(root, bg=self.ui_settings.COLORS['bg'])

        # Set the initial size of the window
        # You might need to adjust these dimensions (e.g., "800x700") based on your content and font sizes
        self.root.geometry("800x800")
        self.root.minsize(800, 700) # Optional: set a minimum size if you want to prevent it from getting too small

        self._create_menu_widgets()

    def _create_menu_widgets(self):
        """Crea los widgets del menú principal."""
        font_ui_bold_tuple = (self.ui_settings.MAIN_FONT_FAMILY, self.ui_settings.UI_FONT_SIZE, "bold")

        # Configure grid for frame_menu
        self.frame_menu.grid_rowconfigure(0, weight=0) # Row for music button
        self.frame_menu.grid_rowconfigure(1, weight=0) # Row for how to play button
        self.frame_menu.grid_rowconfigure(2, weight=1) # Row for logo and other buttons (main content)
        self.frame_menu.grid_columnconfigure(0, weight=1) # Column for left-aligned buttons
        self.frame_menu.grid_columnconfigure(1, weight=1) # Column for right-aligned buttons

        # Botón de Música en la esquina superior izquierda, ahora en la fila 0
        self.button_music_menu = tk.Button(
            self.frame_menu, text="Música: ON", command=self.on_music_toggle_callback,
            font=font_ui_bold_tuple, bg=self.ui_settings.COLORS['button_bg'], fg=self.ui_settings.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2, width=10 # Adjusted width to fit
        )
        self.button_music_menu.grid(row=0, column=0, padx=10, pady=10, sticky="nw") # Top-left corner, row 0

        # Botón "Cómo Jugar" en la esquina superior izquierda, ahora en la fila 1 (debajo de Música)
        self.button_how_to_play_menu = tk.Button(
            self.frame_menu, text="?", command=self.on_how_to_play_menu_click,
            font=font_ui_bold_tuple, bg=self.ui_settings.COLORS['button_bg'], fg=self.ui_settings.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2, width=2, height=1 # Smaller width/height for square look
        )
        self.button_how_to_play_menu.grid(row=1, column=0, padx=10, pady=5, sticky="nw") # Below Music button, row 1

        # Botón "Puntajes" en la esquina superior derecha (sin lógica implementada)
        self.button_scores_menu = tk.Button(
            self.frame_menu, text="Puntajes", command=None, # No logic implemented
            font=font_ui_bold_tuple, bg=self.ui_settings.COLORS['button_bg'], fg=self.ui_settings.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2, width=10
        )
        self.button_scores_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ne") # Top-right corner (still row 0)


        # Frame para contener el logo y los demás botones, centrado
        main_content_frame = tk.Frame(self.frame_menu, bg=self.ui_settings.COLORS['bg'])
        # This frame now spans both columns to be centered
        main_content_frame.grid(row=2, column=0, columnspan=2, sticky="nsew") # Placed in row 2
        main_content_frame.grid_rowconfigure(0, weight=0) # For logo
        main_content_frame.grid_rowconfigure(1, weight=1) # For buttons, give more weight to center them
        main_content_frame.grid_columnconfigure(0, weight=1)


        try:
            if os.path.exists(self.ui_settings.LOGO_PATH):
                original_image = Image.open(self.ui_settings.LOGO_PATH)
                # Redimensionar la imagen para ajustarse al tamaño máximo
                original_image.thumbnail((self.ui_settings.LOGO_MAX_WIDTH, self.ui_settings.LOGO_MAX_HEIGHT), Image.Resampling.LANCZOS)
                self.logo_tk_image = ImageTk.PhotoImage(original_image)
                logo_label = tk.Label(main_content_frame, image=self.logo_tk_image, bg=self.ui_settings.COLORS['bg'])
                logo_label.pack(pady=20)
            else:
                print(f"Advertencia: Archivo de logo no encontrado en '{self.ui_settings.LOGO_PATH}'.")
        except Exception as e:
            print(f"Error al cargar la imagen del logo: {e}")

        # Botón "Nueva Partida" (antes "Iniciar Juego")
        self.button_start_game = tk.Button(
            main_content_frame, text="Nueva Partida", command=self.on_start_game_callback,
            font=font_ui_bold_tuple, bg=self.ui_settings.COLORS['button_bg'], fg=self.ui_settings.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2, width=20
        )
        self.button_start_game.pack(pady=5)

        # Botón "Cargar Partida"
        self.button_load_game = tk.Button(
            main_content_frame, text="Cargar Partida", command=self.on_load_game_callback,
            font=font_ui_bold_tuple, bg=self.ui_settings.COLORS['button_bg'], fg=self.ui_settings.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2, width=20
        )
        self.button_load_game.pack(pady=5)

        # Botón "Volver a seleccionar juego" (sin lógica implementada), ahora debajo de "Cargar Partida"
        self.button_back_to_game_select = tk.Button(
            main_content_frame, text="Volver a seleccionar juego", command=None, # No logic implemented
            font=font_ui_bold_tuple, bg=self.ui_settings.COLORS['button_bg'], fg=self.ui_settings.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2, width=25 # Increased width for longer text
        )
        self.button_back_to_game_select.pack(pady=5)

        self.button_exit_game = tk.Button(
            main_content_frame, text="Salir", command=self.root.quit,
            font=font_ui_bold_tuple, bg=self.ui_settings.COLORS['button_bg'], fg=self.ui_settings.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2, width=20
        )
        self.button_exit_game.pack(pady=5)

    def show_menu_interface(self):
        """Muestra el frame del menú principal y oculta otros.
        Asegura que el frame del menú es el único elemento expansible."""
        # Primero, intentar "desconfigurar" las filas y columnas configuradas para el juego
        # para evitar conflictos si el juego fue mostrado antes.
        try:
            self.root.grid_columnconfigure(0, weight=0)
            self.root.grid_columnconfigure(1, weight=0)
            self.root.grid_rowconfigure(0, weight=0)
            self.root.grid_rowconfigure(1, weight=0)
            self.root.grid_rowconfigure(2, weight=0)
        except tk.TclError:
            pass

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        # Ensure columnspan is applied correctly when showing the menu
        self.frame_menu.grid(row=0, column=0, sticky='nsew', padx=20, pady=20, columnspan=2)


    def hide_menu_interface(self):
        """Oculta el frame del menú principal."""
        self.frame_menu.grid_remove()

    def enable_start_button(self):
        """Habilita el botón de iniciar juego."""
        if self.button_start_game:
             self.button_start_game.config(state='normal')
        if self.button_load_game: # Habilitar también el botón de cargar
            self.button_load_game.config(state='normal')

    def disable_start_button(self):
        """Deshabilita el botón de iniciar juego."""
        if self.button_start_game:
            self.button_start_game.config(state='disabled')
        if self.button_load_game: # Deshabilitar también el botón de cargar
            self.button_load_game.config(state='disabled')

    def update_music_button_text(self, text: str):
        """Actualiza el texto del botón de música en la interfaz del menú."""
        self.button_music_menu.config(text=text)