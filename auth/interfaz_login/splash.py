import customtkinter as ctk
from PIL import Image
import os

CARPETA_RECURSOS = "recursos"

def crear_splash(root):
    splash_frame = ctk.CTkFrame(root, fg_color="black")
    splash_frame.grid(row=0, column=0, rowspan=10, sticky="nsew")

    imagen_estudio = Image.open(os.path.join(CARPETA_RECURSOS, "myfirstchamba.png"))
    splash_img = ctk.CTkImage(imagen_estudio, size=(400, 300))
    ctk.CTkLabel(splash_frame, image=splash_img, text="").pack(expand=True)

    return splash_frame
