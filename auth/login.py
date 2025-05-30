import customtkinter as ctk
from PIL import Image
import os

from auth.utils import asegurar_estructura_directorios
from auth.interfaz_login.window_config import configurar_ventana
from auth.interfaz_login.layout import configurar_layout
from auth.interfaz_login.fade import fade_in
from auth.interfaz_login.formulario import mostrar_formulario
from menus import seleccion_juego
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from constants import RECURSOS_DIR

def mostrar_login():
    asegurar_estructura_directorios()

    root = ctk.CTk()
    configurar_ventana(root)
    configurar_layout(root)

    splash_frame = ctk.CTkFrame(root, fg_color="black")
    splash_frame.grid(row=0, column=0, rowspan=10, sticky="nsew")

    splash_img = ctk.CTkImage(Image.open(os.path.join(RECURSOS_DIR, "myfirstchamba.png")), size=(500, 500))
    ctk.CTkLabel(splash_frame, image=splash_img, text="").pack(expand=True)

    fade_in(root, splash_frame, lambda: mostrar_formulario(root, mostrar_login))

    root.mainloop()