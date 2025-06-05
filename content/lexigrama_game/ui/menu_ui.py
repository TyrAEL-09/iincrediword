# ui/menu_ui.py
import tkinter as tk
from PIL import Image, ImageTk
import os

class MenuUI:
    """Gestiona la creación y actualización de la interfaz de usuario del menú principal."""

    # --- Inicialización y configuración ---
    def __init__(self, root: tk.Tk, ui_settings, on_start_game, on_music_toggle, on_back_menu, on_how_to_play_menu_click, on_load_game, on_show_scores):
        self.root = root
        self.ui_settings = ui_settings
        self.on_start_game_callback = on_start_game
        self.on_music_toggle_callback = on_music_toggle
        self.on_back_menu_callback = on_back_menu
        self.on_how_to_play_menu_click = on_how_to_play_menu_click
        self.on_load_game_callback = on_load_game
        self.on_show_scores = on_show_scores

        self.logo_tk_image = None
        self.frame_menu = tk.Frame(root, bg=self.ui_settings.COLORS['bg'])

        # Configuración de ventana
        self.root.geometry("800x800") 
        self.root.minsize(800, 700) 

        self._create_menu_widgets()
        self.show_menu_interface()

    # --- Creación de widgets ---
    def _create_menu_widgets(self):
        """Crea los widgets del menú principal solo con botones de imagen."""
        boton_img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../recursos/boton_gris.png"))
        boton_hover_img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../recursos/boton_cyan.png"))

        # Limpiar frame por si se recrea
        for widget in self.frame_menu.winfo_children():
            widget.destroy()

        # Frame superior para los botones de las esquinas
        self.top_buttons_frame = tk.Frame(self.frame_menu, bg=self.ui_settings.COLORS['bg'])
        self.top_buttons_frame.pack(fill="x", side="top", pady=(10, 0))

        # Frame para los botones de la izquierda
        self.left_buttons_frame = tk.Frame(self.top_buttons_frame, bg=self.ui_settings.COLORS['bg'])
        self.left_buttons_frame.pack(side="left", anchor="nw", padx=(10, 0))

        # Logo
        try:
            if os.path.exists(self.ui_settings.LOGO_PATH):
                original_image = Image.open(self.ui_settings.LOGO_PATH)
                original_image.thumbnail((self.ui_settings.LOGO_MAX_WIDTH, self.ui_settings.LOGO_MAX_HEIGHT), Image.Resampling.LANCZOS)
                self.logo_tk_image = ImageTk.PhotoImage(original_image)
                # Cambia pady para subir la imagen más arriba
                logo_label = tk.Label(self.frame_menu, image=self.logo_tk_image, bg=self.ui_settings.COLORS['bg'])
                logo_label.pack(pady=(5, 10))  # Antes: pady=20. Ahora: pady=(5, 10)
            else:
                print(f"Advertencia: Archivo de logo no encontrado en '{self.ui_settings.LOGO_PATH}'.")
        except Exception as e:
            print(f"Error al cargar la imagen del logo: {e}")
        
        # Botones del menú
        # Botón "¿Cómo Jugar?"
        self.button_how_to_play_menu = self._create_image_button(
            self.left_buttons_frame, boton_img_path, "¿Cómo Jugar?", self.on_how_to_play_menu_click, width=180, height=45, hover_image_path=boton_hover_img_path
        )
        self.button_how_to_play_menu.pack(side="top", pady=(0, 2))

        # Botón de música (esquina superior izquierda)
        self.button_music_menu = self._create_image_button(
            self.left_buttons_frame, boton_img_path, "Música: ON", self.on_music_toggle_callback, width=180, height=45, hover_image_path=boton_hover_img_path
        )
        self.button_music_menu.pack(side="top", pady=(2, 0))

        # Botón "Puntajes"
        self.button_scores = self._create_image_button(
            self.top_buttons_frame, boton_img_path, "Puntajes", self.on_show_scores, width=180, height=45, hover_image_path=boton_hover_img_path
        )
        self.button_scores.pack(side="right", padx=(0, 20), pady=(0, 2))

        # Botón "Nueva Partida"
        self.button_start_game = self._create_image_button(
            self.frame_menu, boton_img_path, "Nueva Partida", self.on_start_game_callback, width=250, height=55, hover_image_path=boton_hover_img_path
        )
        self.button_start_game.pack(pady=(0, 5))  # Antes: pady=5. Ahora: pady=(0, 5)

        # Botón "Cargar Partida"
        self.button_load_game = self._create_image_button(
            self.frame_menu, boton_img_path, "Cargar Partida", self.on_load_game_callback, width=250, height=55, hover_image_path=boton_hover_img_path
        )
        self.button_load_game.pack(pady=5)

        # Botón "Volver a seleccionar juego"
        self.button_back_to_game_select = self._create_image_button(
            self.frame_menu, boton_img_path, "Volver a seleccionar juego", self.on_back_menu_callback, width=300, height=55, hover_image_path=boton_hover_img_path
        )
        self.button_back_to_game_select.pack(pady=5)

        # Botón "Salir"
        self.button_exit_game = self._create_image_button(
            self.frame_menu, boton_img_path, "Salir", self._exit_app, width=250, height=55, hover_image_path=boton_hover_img_path
        )
        self.button_exit_game.pack(pady=(5, 10))  # Antes: pady=10. Ahora: pady=(5, 10)

    def _create_image_button(self, parent, image_path, text, command, width=150, height=50, hover_image_path=None):
        """Crea un botón personalizado usando Canvas con imagen y texto, con efecto hover."""
        canvas = tk.Canvas(parent, width=width, height=height, highlightthickness=0, bg=self.ui_settings.COLORS['bg'])
        try:
            img = Image.open(image_path)
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            canvas.normal_img = tk_img 
            canvas.create_image(0, 0, anchor='nw', image=tk_img)
        except Exception as e:
            print(f"Error al cargar imagen para botón: {e}")

        # Imagen hover
        if hover_image_path:
            try:
                hover_img = Image.open(hover_image_path)
                hover_img = hover_img.resize((width, height), Image.Resampling.LANCZOS)
                tk_hover_img = ImageTk.PhotoImage(hover_img)
                canvas.hover_img = tk_hover_img
            except Exception as e:
                print(f"Error al cargar imagen hover para botón: {e}")
                canvas.hover_img = None
        else:
            canvas.hover_img = None

        # Texto centrado
        canvas.text_id = canvas.create_text(width//2, height//2, text=text, fill=self.ui_settings.COLORS['button_fg'],
                          font=(self.ui_settings.MAIN_FONT_FAMILY, self.ui_settings.UI_FONT_SIZE, "bold"))

        # Guardar el comando y estado
        canvas.command = command
        canvas.state = "normal"

        # Evento de click
        def on_click(event=None):
            if canvas.state == "normal" and callable(canvas.command):
                canvas.command()
        canvas.bind("<Button-1>", on_click)

        # Efecto hover con imagen
        def on_enter(e):
            if canvas.state == "normal":
                canvas.config(cursor="hand2")
                if canvas.hover_img:
                    canvas.itemconfig(1, image=canvas.hover_img)
        def on_leave(e):
            if canvas.state == "normal":
                canvas.config(cursor="")
                if hasattr(canvas, 'normal_img'):
                    canvas.itemconfig(1, image=canvas.normal_img)
        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)

        # Permitir habilitar/deshabilitar
        def config_proxy(**kwargs):
            if "state" in kwargs:
                canvas.state = kwargs["state"]
                if canvas.state == "disabled":
                    canvas.config(cursor="arrow")
                else:
                    canvas.config(cursor="")
        canvas.config = config_proxy

        return canvas

    # --- Métodos de interfaz pública ---
    def show_menu_interface(self):
        """Muestra el frame del menú principal y oculta otros."""
        self.frame_menu.pack(expand=True, fill="both")

    def hide_menu_interface(self):
        """Oculta el frame del menú principal."""
        self.frame_menu.pack_forget()

    def enable_start_button(self):
        """Habilita el botón de iniciar juego y cargar partida."""
        if self.button_start_game:
            self.button_start_game.config(state='normal')
        if self.button_load_game:
            self.button_load_game.config(state='normal')

    def disable_start_button(self):
        """Deshabilita el botón de iniciar juego y cargar partida."""
        if self.button_start_game:
            self.button_start_game.config(state='disabled')
        if self.button_load_game:
            self.button_load_game.config(state='disabled')

    def update_music_button_text(self, text: str):
        """Actualiza el texto del botón de música en la interfaz del menú."""
        if hasattr(self, "button_music_menu"):
            if "ON" in text:
                self.button_music_menu.itemconfig(self.button_music_menu.text_id, text="Música: ON")
            else:
                self.button_music_menu.itemconfig(self.button_music_menu.text_id, text="Música: OFF")

    def _exit_app(self):
        import os
        os._exit(0)