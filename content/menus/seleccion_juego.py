import customtkinter as ctk
from PIL import Image
import os
from Hexa_Link.run_game import iniciar_hexalink
from LexicoGrama.lexicograma import iniciar_lexicograma

# Ruta absoluta a la carpeta recursos
CARPETA_RECURSOS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recursos")

class MenuSeleccionJuego:
    def __init__(self, usuario):
        self.usuario = usuario
        self.root = ctk.CTk()
        self.root.title("Seleccionar Juego")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_total)

        self.construir_interfaz()
        self.root.mainloop()

    def cerrar_total(self):
        self.root.destroy()
        os._exit(0)

    def construir_interfaz(self):
        fondo = ctk.CTkFrame(self.root, corner_radius=0)
        fondo.pack(fill="both", expand=True)

        # Configurar layout del fondo
        fondo.rowconfigure(1, weight=1)
        fondo.columnconfigure(0, weight=1)

        # Título
        titulo = ctk.CTkLabel(
            fondo,
            text="Selecciona un juego",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#00BFFF"
        )
        titulo.grid(row=0, column=0, pady=(20, 10), sticky="n")

        # Contenedor de juegos
        contenedor_juegos = ctk.CTkFrame(
            fondo,
            fg_color="#1e2a38",
            corner_radius=15,
            border_width=2,
            border_color="#0e1521"
        )
        contenedor_juegos.grid(row=1, column=0, padx=30, sticky="n")

        # Cargar imágenes usando ruta absoluta y guardarlas como atributos de instancia
        imagen_path_hexalink = os.path.join(CARPETA_RECURSOS, "hexalink.png")
        self.imagen_hexalink = ctk.CTkImage(dark_image=Image.open(imagen_path_hexalink), size=(150, 150))

        imagen_path_lexicograma = os.path.join(CARPETA_RECURSOS, "lexicograma.png")
        self.imagen_lexicograma = ctk.CTkImage(dark_image=Image.open(imagen_path_lexicograma), size=(150, 150))

        # Botones de juego
        juegos_frame = ctk.CTkFrame(contenedor_juegos, fg_color="transparent")
        juegos_frame.pack(pady=20, padx=20)

        boton_hexalink = ctk.CTkButton(
            juegos_frame,
            image=self.imagen_hexalink,
            text="",
            width=150,
            height=150,
            fg_color="#004f7c",
            hover_color="#007acc",
            border_width=3,
            border_color="#00bfff",
            corner_radius=20,
            command=self.abrir_hexalink
        )
        boton_hexalink.grid(row=0, column=0, padx=30, pady=5)

        etiqueta_hexalink = ctk.CTkLabel(
            juegos_frame,
            text="Hexa-Link",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00BFFF"
        )
        etiqueta_hexalink.grid(row=1, column=0, pady=(5, 15))

        boton_lexicograma = ctk.CTkButton(
            juegos_frame,
            image=self.imagen_lexicograma,
            text="",
            width=150,
            height=150,
            fg_color="#004f7c",
            hover_color="#007acc",
            border_width=3,
            border_color="#00bfff",
            corner_radius=20,
            command=self.abrir_lexicograma
        )
        boton_lexicograma.grid(row=0, column=1, padx=30, pady=5)

        etiqueta_lexicograma = ctk.CTkLabel(
            juegos_frame,
            text="Lexicograma",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00BFFF"
        )
        etiqueta_lexicograma.grid(row=1, column=1, pady=(5, 15))

        # Botón salir del juego al fondo
        boton_salir = ctk.CTkButton(
            fondo,
            text="Salir del juego",
            width=180,
            height=45,
            fg_color="#d93025",
            hover_color="#a52714",
            corner_radius=25,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.salir_juego
        )
        boton_salir.grid(row=2, column=0, pady=(10, 60), sticky="s")

    def abrir_hexalink(self):
        # Solución: destruir la ventana antes de abrir el menú HexaLink y pasar None como parent_root
        self.root.destroy()
        from menus.menu_hexalink import MenuHexaLink
        MenuHexaLink(self.usuario, None)

    def abrir_lexicograma(self):
        self.root.destroy()
        iniciar_lexicograma(self.usuario)

    def salir_juego(self):
        # Forzar cierre inmediato del proceso y la terminal sin destroy para evitar bloqueos de Tkinter
        import os
        os._exit(0)

def iniciar_menu(usuario):
    import tkinter as tk
    if tk._default_root:
        try:
            tk._default_root.destroy()
        except Exception:
            pass
    MenuSeleccionJuego(usuario)