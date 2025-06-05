import customtkinter as ctk
from PIL import Image
import os
from Hexa_Link.run_game import iniciar_hexalink
from lexigrama.lexicograma import iniciar_lexicograma

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
        # Usar self.fondo para poder destruirlo después
        if hasattr(self, "fondo") and self.fondo is not None:
            self.fondo.destroy()
        self.fondo = ctk.CTkFrame(self.root, corner_radius=0)
        self.fondo.pack(fill="both", expand=True)
        fondo = self.fondo

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

        imagen_path_lexicograma = os.path.join(CARPETA_RECURSOS, "lexigrama.png")
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
            text="Lexigrama",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00BFFF"
        )
        etiqueta_lexicograma.grid(row=1, column=1, pady=(5, 15))

        # Botón Créditos debajo de los juegos
        boton_creditos = ctk.CTkButton(
            fondo,
            text="Créditos",
            width=180,
            height=38,
            fg_color="#00BFFF",
            hover_color="#007acc",
            corner_radius=20,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.mostrar_creditos
        )
        boton_creditos.grid(row=2, column=0, pady=(10, 0), sticky="n")

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
        boton_salir.grid(row=3, column=0, pady=(10, 60), sticky="s")

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
    
    def mostrar_creditos(self):
        import tkinter as tk
        from PIL import Image, ImageTk, ImageFont, ImageDraw

        # Destruir el frame principal y crear uno nuevo para los créditos
        if hasattr(self, "fondo") and self.fondo is not None:
            self.fondo.destroy()
        self.fondo = ctk.CTkFrame(self.root, corner_radius=0, fg_color="#181f29")
        self.fondo.pack(fill="both", expand=True)
        fondo = self.fondo

        # Leer el texto de créditos
        creditos_path = os.path.join(CARPETA_RECURSOS, "creditos.txt")
        with open(creditos_path, "r", encoding="utf-8") as f:
            creditos_texto = f.read()

        # Fuente personalizada
        fuente_path = os.path.join(CARPETA_RECURSOS, "Jersey20-Regular.ttf")
        font_size = 22

        # Renderizar el texto en una imagen usando la fuente personalizada
        font = ImageFont.truetype(fuente_path, font_size)
        lines = creditos_texto.splitlines()
        img_width = 540
        line_height = font_size + 6
        img_height = max(600, line_height * len(lines) + 40)
        img = Image.new("RGBA", (img_width, img_height), (24, 31, 41, 255))
        draw = ImageDraw.Draw(img)
        y = 20
        for line in lines:
            # Centrar cada línea horizontalmente usando getbbox
            bbox = font.getbbox(line)
            line_width = bbox[2] - bbox[0]
            x = (img_width - line_width) // 2
            draw.text((x, y), line, font=font, fill="#00BFFF")
            y += line_height
        texto_img_tk = ImageTk.PhotoImage(img)

        # Cargar imagen al final (animación)
        img_path = os.path.join(CARPETA_RECURSOS, "myfirstchamba.png")
        img_final = Image.open(img_path).resize((220, 220), Image.LANCZOS)
        img_final_tk = ImageTk.PhotoImage(img_final)

        # Canvas de tkinter (NO customtkinter)
        canvas = tk.Canvas(fondo, width=img_width, height=500, bg="#181f29", highlightthickness=0, bd=0)
        canvas.pack(pady=(20, 0))
        texto_img_id = canvas.create_image(0, 0, anchor="nw", image=texto_img_tk)
        img_final_id = canvas.create_image(img_width//2, img_height + 120, anchor="center", image=img_final_tk)

        # Mantener referencias para evitar garbage collection
        canvas.texto_img_tk = texto_img_tk
        canvas.img_final_tk = img_final_tk

        # Scroll animado hasta que la imagen esté centrada
        ventana_alto = 500
        img_final_alto = 220
        img_centro_y = img_height + 120
        offset_final = img_centro_y - (ventana_alto // 2)
        scroll_speed = 1  # píxel por frame

        def scroll_step(offset=0):
            # Verifica que el canvas siga existiendo antes de manipularlo
            if not canvas.winfo_exists():
                return
            canvas.yview_moveto(offset / (img_height + 240))
            if offset < offset_final:
                self.root.after(35, lambda: scroll_step(offset + scroll_speed))
            else:
                canvas.yview_moveto(offset_final / (img_height + 240))

        canvas.config(scrollregion=(0, 0, img_width, img_height + 240))
        scroll_step(0)

        # Botón volver (customtkinter)
        btn_volver = ctk.CTkButton(
            fondo,
            text="Volver",
            width=120,
            height=40,
            fg_color="#00BFFF",
            hover_color="#007acc",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.construir_interfaz
        )
        btn_volver.pack(pady=18)

def iniciar_menu(usuario):
    import tkinter as tk
    if tk._default_root:
        try:
            tk._default_root.destroy()
        except Exception:
            pass
    MenuSeleccionJuego(usuario)