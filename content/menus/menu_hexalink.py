import customtkinter as ctk
import os
import subprocess
import sys
from PIL import Image
from utils.ui_utils import sonido_click

# Ruta de la imagen del logo de Hexa-Link
HEXALINK_IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'recursos', 'hexalink.png')

class MenuHexaLink:
    """
    Menú principal de Hexa-Link.
    Permite al usuario cargar partida, iniciar nueva, volver al menú de selección o salir.
    """

    def __init__(self, usuario, parent_root):
        """
        Inicializa el menú de Hexa-Link.
        Args:
            usuario (str): Nombre de usuario actual.
            parent_root (CTk | None): Ventana padre, si existe.
        Uso: Se invoca desde el menú de selección de juegos.
        """
        self.usuario = usuario
        self.parent_root = parent_root
        self.root = ctk.CTk()
        self.root.title("Hexa-Link")
        self.root.geometry("540x480")
        self.root.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.root.configure(bg="#23272e")
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_total)
        self.hexalink_img = self.cargar_imagen()
        self.construir_interfaz()
        self.root.mainloop()
        if self.parent_root is not None:
            try:
                self.parent_root.destroy()
            except Exception:
                pass

    def cargar_imagen(self):
        """
        Carga la imagen del logo de Hexa-Link como CTkImage.
        Returns:
            CTkImage | None: Imagen cargada o None si no existe.
        Uso: Solo en este menú.
        """
        if os.path.exists(HEXALINK_IMG_PATH):
            pil_img = Image.open(HEXALINK_IMG_PATH).resize((140, 140), Image.NEAREST)
            return ctk.CTkImage(dark_image=pil_img, size=(140, 140))
        return None

    def cerrar_total(self):
        """
        Cierra completamente la aplicación.
        Uso: Al cerrar la ventana principal del menú.
        """
        self.root.destroy()
        os._exit(0)

    def construir_interfaz(self):
        """
        Construye y organiza todos los widgets del menú principal.
        Uso: Solo en la inicialización del menú.
        """
        # --- Marco central estilo pixelart ---
        marco = ctk.CTkFrame(
            self.root,
            width=420,
            height=410,
            corner_radius=0,
            fg_color="#222831",
            border_width=5,
            border_color="#00FFF7"
        )
        marco.place(relx=0.5, rely=0.5, anchor="center")

        # --- Logo o título ---
        if self.hexalink_img:
            img_label = ctk.CTkLabel(
                marco,
                text="",
                image=self.hexalink_img,
                fg_color="transparent"
            )
            img_label.pack(pady=(18, 6))
        else:
            titulo = ctk.CTkLabel(
                marco,
                text="Hexa-Link",
                font=ctk.CTkFont(family="Consolas", size=32, weight="bold"),
                text_color="#00FFF7"
            )
            titulo.pack(pady=(18, 6))

        # --- Estilo de botones pixelart ---
        btn_style = {
            "width": 260,
            "height": 48,
            "corner_radius": 0,
            "font": ctk.CTkFont(family="Consolas", size=18, weight="bold"),
            "border_width": 4,
            "border_color": "#00FFF7",
            "text_color": "#F8F8F8",
        }

        def with_sound(cmd):
            """
            Decorador para reproducir sonido al pulsar un botón.
            Args:
                cmd (callable): Función a ejecutar.
            Returns:
                callable: Función decorada.
            Uso: Para todos los botones del menú.
            """
            def wrapper(*args, **kwargs):
                sonido_click()
                return cmd(*args, **kwargs)
            return wrapper

        # --- Botón: Cargar partida guardada ---
        ctk.CTkButton(
            marco, text="Cargar partida", fg_color="#393E46", hover_color="#00FFF7",
            **btn_style, command=with_sound(self.cargar_partida)
        ).pack(pady=(8, 8))

        # --- Botón: Nueva partida ---
        ctk.CTkButton(
            marco, text="Nueva partida", fg_color="#393E46", hover_color="#00FFF7",
            **btn_style, command=with_sound(self.nueva_partida)
        ).pack(pady=(0, 8))

        # --- Botón: Volver al menú de selección de juegos ---
        ctk.CTkButton(
            marco, text="Volver a seleccionar juego", fg_color="#222831", hover_color="#00FFF7",
            **btn_style, command=with_sound(self.volver_seleccion)
        ).pack(pady=(0, 8))

        # --- Botón: Salir del juego ---
        ctk.CTkButton(
            marco, text="Salir", fg_color="#d90429", hover_color="#a52714",
            **btn_style, command=with_sound(self.salir)
        ).pack(pady=(0, 16))

        # --- Botón: Ver puntajes (arriba a la derecha) ---
        ctk.CTkButton(
            self.root, text="Puntajes", width=110, height=36, fg_color="#00FFF7", hover_color="#393E46",
            text_color="#222831", corner_radius=0, font=ctk.CTkFont(family="Consolas", size=15, weight="bold"),
            border_width=4, border_color="#00FFF7", command=with_sound(self.mostrar_tablero_puntajes)
        ).place(relx=1.0, rely=0.0, anchor="ne", x=-18, y=18)

        # --- Botón: Ayuda (arriba a la izquierda) ---
        ctk.CTkButton(
            self.root, text="?", width=36, height=36, fg_color="#00FFF7", hover_color="#393E46",
            text_color="#222831", corner_radius=0, font=ctk.CTkFont(family="Consolas", size=22, weight="bold"),
            border_width=4, border_color="#00FFF7", command=with_sound(self.mostrar_ayuda)
        ).place(relx=0.0, rely=0.0, anchor="nw", x=18, y=18)

    def cargar_partida(self):
        """
        Lanza el juego en modo 'cargar partida'.
        Uso: Botón 'Cargar partida'.
        """
        self.root.destroy()
        working_dir = os.path.dirname(os.path.dirname(__file__))
        subprocess.Popen([sys.executable, '-m', 'Hexa_Link.run_game', self.usuario, 'cargar'], cwd=working_dir)

    def nueva_partida(self):
        """
        Lanza el juego en modo 'nueva partida'.
        Uso: Botón 'Nueva partida'.
        """
        self.root.destroy()
        working_dir = os.path.dirname(os.path.dirname(__file__))
        subprocess.Popen([sys.executable, '-m', 'Hexa_Link.run_game', self.usuario, 'nueva'], cwd=working_dir)

    def volver_seleccion(self):
        """
        Vuelve al menú de selección de juegos.
        Uso: Botón 'Volver a seleccionar juego'.
        """
        self.root.destroy()
        from menus.seleccion_juego import iniciar_menu
        iniciar_menu(self.usuario)

    def salir(self):
        """
        Sale completamente del juego y cierra la ventana padre si existe.
        Uso: Botón 'Salir'.
        """
        self.root.destroy()
        if self.parent_root:
            self.parent_root.destroy()
        # No llamar a os._exit(0): la consola se cerrará automáticamente cuando no haya ventanas Tkinter activas

    def mostrar_tablero_puntajes(self):
        """
        Muestra una ventana con el top 10 de puntajes.
        Uso: Botón 'Puntajes'.
        """
        import json
        scores_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Hexa_Link", "scores.json")
        try:
            if os.path.exists(scores_path):
                with open(scores_path, "r", encoding="utf-8") as f:
                    scores = json.load(f)
            else:
                scores = []
        except Exception:
            scores = []
        scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
        win = ctk.CTkToplevel(self.root)
        win.title("Top 10 Puntajes")
        win.geometry("420x420")
        win.resizable(False, False)
        win.configure(fg_color="#1e2a38")
        titulo = ctk.CTkLabel(win, text="Top 10 Puntajes", font=ctk.CTkFont(size=22, weight="bold"), text_color="#00BFFF")
        titulo.pack(pady=(22, 10))
        for idx, entry in enumerate(scores):
            usuario = entry["usuario"]
            puntaje = entry["score"]
            color = "#FFD700" if idx == 0 else "#FFFFFF"
            fila = ctk.CTkLabel(win, text=f"{idx+1}. {usuario} - {puntaje}", font=ctk.CTkFont(size=17, weight="bold"), text_color=color)
            fila.pack(anchor="w", padx=38, pady=(0, 2))
        ctk.CTkButton(win, text="Cerrar", width=120, height=36, fg_color="#00BFFF", hover_color="#007acc",
                      corner_radius=16, font=ctk.CTkFont(size=15, weight="bold"), command=win.destroy).pack(pady=24)

    def mostrar_ayuda(self):
        """
        Muestra una ventana con las instrucciones del juego.
        Uso: Botón '?'.
        """
        win = ctk.CTkToplevel(self.root)
        win.title("¿Cómo se juega Hexa-Link?")
        win.geometry("540x480")
        win.resizable(False, False)
        win.configure(fg_color="#1e2a38")
        titulo = ctk.CTkLabel(win, text="¿Cómo se juega Hexa-Link?", font=ctk.CTkFont(size=22, weight="bold"), text_color="#00BFFF")
        titulo.pack(pady=(22, 10))
        explicacion = (
            "• El objetivo es formar palabras válidas usando las letras del\ntablero.\n"
            "• Cada palabra debe tener al menos 3 letras y contener la letra \ncentral obligatoriamente.\n"
            "• Cada letra usada vale 20 puntos.\n"
            "• Si logras formar varias palabras seguidas sin fallar, se activa \nel sistema de combos:\n"
            "    - Combo x1.25 a partir de 2 palabras seguidas.\n"
            "    - Combo x1.5 a partir de 6 palabras seguidas.\n"
            "    - Combo x2 a partir de 10 palabras seguidas.\n"
            "• El color del fuego de la animación cambia según tu combo:\n"
            "    - Normal: combo < 5\n"
            "    - Azul: combo 5 a 9\n"
            "    - Violeta: combo 10 o más\n"
            "• Puedes pausar el juego, guardar tu partida y unpausela luego.\n"
            "• El botón de música permite activar/desactivar la música de \nfondo.\n"
            "• Al completar todas las palabras, verás tu puntaje y el ranking \nde los mejores.\n"
            "\n¡Buena suerte consiguiendo el mejor puntaje! :)"
        )
        texto = ctk.CTkTextbox(win, width=480, height=340, font=ctk.CTkFont(size=16), fg_color="#1e2a38", text_color="#FFFFFF")
        texto.insert("1.0", explicacion)
        texto.configure(state="disabled")
        texto.pack(padx=20, pady=(0, 18))
        ctk.CTkButton(win, text="Cerrar", width=120, height=36, fg_color="#00BFFF", hover_color="#007acc",
                      corner_radius=16, font=ctk.CTkFont(size=15, weight="bold"), command=win.destroy).pack(pady=8)
