import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os

# Importación segura de módulos de juegos
try:
    from Hexa_Link import hexalink
except ImportError:
    hexalink = None

try:
    from LexicoGrama import lexicograma
except ImportError:
    lexicograma = None

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

CARPETA_RECURSOS = "recursos"

def mostrar_menu(usuario):
    ventana = ctk.CTk()
    ventana.title("Seleccionar Juego")
    ventana.geometry("600x500")
    ventana.minsize(400, 350)

    for i in range(10):
        ventana.rowconfigure(i, weight=1)
    ventana.columnconfigure((0, 1), weight=1)

    ctk.CTkLabel(
        ventana,
        text=f"Bienvenido, {usuario}",
        font=ctk.CTkFont(size=20, weight="bold")
    ).grid(row=0, column=0, columnspan=2, pady=(10, 0))

    ctk.CTkLabel(
        ventana,
        text="Selecciona un juego",
        font=ctk.CTkFont(size=16)
    ).grid(row=1, column=0, columnspan=2, pady=(5, 20))

    def jugar_hexalink():
        if hexalink and hasattr(hexalink, "iniciar_juego"):
            ventana.destroy()
            hexalink.iniciar_juego(usuario)
        else:
            messagebox.showerror("Error", "El juego Hexa-Link no está disponible.")

    def jugar_lexicograma():
        if lexicograma and hasattr(lexicograma, "iniciar_juego"):
            ventana.destroy()
            lexicograma.iniciar_juego(usuario)
        else:
            messagebox.showerror("Error", "El juego Lexicograma no está disponible.")

    # Cargar imágenes
    ruta_hexalink = os.path.join(CARPETA_RECURSOS, "hexalink.jpg")
    ruta_lexico = os.path.join(CARPETA_RECURSOS, "hexalink.jpg")

    try:
        imagen_hexalink = ctk.CTkImage(Image.open(ruta_hexalink), size=(370, 200))
    except Exception:
        imagen_hexalink = None

    try:
        imagen_lexico = ctk.CTkImage(Image.open(ruta_lexico), size=(370, 200))
    except Exception:
        imagen_lexico = None

    # Botón de Hexa-Link con imagen
    ctk.CTkButton(
        ventana,
        text="",
        image=imagen_hexalink,
        width=200,
        height=200,
        command=jugar_hexalink
    ).grid(row=2, column=0, padx=20, pady=10)

    # Botón de Lexicograma con imagen
    ctk.CTkButton(
        ventana,
        text="",
        image=imagen_lexico,
        width=200,
        height=200,
        command=jugar_lexicograma
    ).grid(row=2, column=1, padx=20, pady=10)

    # Botón de salir
    ctk.CTkButton(
        ventana,
        text="Salir",
        font=ctk.CTkFont(size=14),
        height=30,
        command=ventana.destroy
    ).grid(row=4, column=0, columnspan=2, pady=30)

    ventana.mainloop()