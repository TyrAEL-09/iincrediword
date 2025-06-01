# ui/menu_ui.py
import tkinter as tk
# from tkinter import PhotoImage # PhotoImage no se usa directamente, se usa ImageTk.PhotoImage
from PIL import Image, ImageTk
import os # Para verificar la existencia del archivo

class MenuUI:
    """Gestiona la creación y actualización de la interfaz de usuario del menú principal."""

    def __init__(self, root: tk.Tk, ui_settings, on_start_game, on_music_toggle, on_back_menu):
        self.root = root
        self.ui_settings = ui_settings
        self.on_start_game_callback = on_start_game
        self.on_music_toggle_callback = on_music_toggle
        self.on_back_menu_callback = on_back_menu

        self.logo_tk_image = None # Para mantener una referencia a la imagen
        self.frame_menu = tk.Frame(root, bg=self.ui_settings.COLORS['bg'])

        self._create_menu_widgets()

    def _create_menu_widgets(self):
        """Crea los widgets del menú principal."""
        font_ui_bold_tuple = (self.ui_settings.MAIN_FONT_FAMILY, self.ui_settings.UI_FONT_SIZE, "bold")

        # Carga y muestra el logo
        try:
            if os.path.exists(self.ui_settings.LOGO_PATH):
                pil_image = Image.open(self.ui_settings.LOGO_PATH)
                img_width, img_height = pil_image.size
                # Calcular ratio para redimensionar manteniendo aspecto y sin exceder max dimensiones
                ratio = min(self.ui_settings.LOGO_MAX_WIDTH / img_width, self.ui_settings.LOGO_MAX_HEIGHT / img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                resized_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.logo_tk_image = ImageTk.PhotoImage(resized_image) # Guardar referencia
                
                self.label_logo = tk.Label(self.frame_menu, image=self.logo_tk_image, bg=self.ui_settings.COLORS['bg'])
                self.label_logo.pack(pady=(20, 10))
            else:
                # Si no existe el path, lanzar error para que caiga en el fallback
                print(f"Advertencia: No se encontró el archivo de logo '{self.ui_settings.LOGO_PATH}'.")
                raise FileNotFoundError 

        except (FileNotFoundError, Exception) as e: # Captura FileNotFoundError y otros errores de PIL
            print(f"Error al cargar el logo '{self.ui_settings.LOGO_PATH}': {e}. Usando texto de fallback.")
            # Fallback a texto si el logo no se puede cargar
            self.label_logo_fallback = tk.Label(self.frame_menu, text="LEXIGRAMA",
                                                font=(self.ui_settings.MAIN_FONT_FAMILY, 30, "bold"),
                                                bg=self.ui_settings.COLORS['bg'], fg=self.ui_settings.COLORS['fg'])
            self.label_logo_fallback.pack(pady=(20,10))

        # Botón Iniciar Juego
        self.button_start_game = tk.Button(
            self.frame_menu, text="Iniciar Juego", command=self.on_start_game_callback,
            bg=self.ui_settings.COLORS['button_bg'], fg=self.ui_settings.COLORS['button_fg'],
            font=font_ui_bold_tuple, relief=tk.RAISED, borderwidth=2, width=20, height=2
        )
        self.button_start_game.pack(pady=10)

        # Botón Música
        self.button_music_menu = tk.Button(
            self.frame_menu, text="Música: OFF", command=self.on_music_toggle_callback,
            font=font_ui_bold_tuple, bg=self.ui_settings.COLORS['button_bg'], fg=self.ui_settings.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2, width=15
        )
        self.button_music_menu.pack(pady=5)

        # Botón Volver (deshabilitado por defecto)
        self.button_back_menu = tk.Button(
            self.frame_menu, text="Volver", command=self.on_back_menu_callback,
            font=font_ui_bold_tuple, bg=self.ui_settings.COLORS['button_bg'], fg=self.ui_settings.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2, width=15
        )
        self.button_back_menu.pack(pady=(5, 20))
        self.button_back_menu.config(state='disabled') # Por defecto deshabilitado

    def show_menu_interface(self):
        """Muestra el frame del menú principal y oculta otros, 
        asegurando la configuración correcta de la grilla de root."""

        # Restablecer los pesos de las columnas y filas que podrían haber sido 
        # configuradas por otras interfaces (como GameUI).
        # GameUI configura self.root.grid_columnconfigure para las columnas 0 y 1,
        # y self.root.grid_rowconfigure para las filas 0 y 1, con diferentes pesos.
        # Para que MenuUI funcione como se espera (una sola celda principal en root),
        # debemos asegurarnos de que las configuraciones de GameUI no interfieran.

        # Restablecer el peso de la columna 1 (usada por GameUI) a 0.
        # Esto evita que la columna 1 siga ocupando espacio o afectando la distribución.
        try:
            self.root.grid_columnconfigure(1, weight=0)
        except tk.TclError:
            # Puede ocurrir si la columna 1 no fue configurada previamente, lo cual es seguro ignorar.
            pass
            
        # Restablecer el peso de la fila 1 (usada por GameUI) a 0.
        try:
            self.root.grid_rowconfigure(1, weight=0)
        except tk.TclError:
            # Puede ocurrir si la fila 1 no fue configurada previamente, lo cual es seguro ignorar.
            pass

        # Ahora, configurar la grilla de root para que la celda (0,0) sea la única expansible,
        # que es la configuración que espera el menú principal.
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Colocar el frame_menu en la celda (0,0) de root, 
        # haciendo que se expanda para llenar la celda.
        self.frame_menu.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)


    def hide_menu_interface(self):
        """Oculta el frame del menú principal."""
        self.frame_menu.grid_remove()

    def enable_start_button(self):
        """Habilita el botón de iniciar juego."""
        if self.button_start_game: # Comprobar si el botón existe
             self.button_start_game.config(state='normal')

    def disable_start_button(self):
        """Deshabilita el botón de iniciar juego."""
        if self.button_start_game: # Comprobar si el botón existe
            self.button_start_game.config(state='disabled')

    def update_music_button_text(self, text: str):
        """Actualiza el texto del botón de música en la interfaz del menú."""
        if self.button_music_menu: # Comprobar si el botón existe
            self.button_music_menu.config(text=text)