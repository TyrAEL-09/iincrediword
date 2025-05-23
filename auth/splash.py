import customtkinter as ctk
from PIL import Image
import os

CARPETA_RECURSOS = "recursos"

def mostrar_splash(callback_despues):
    splash = ctk.CTk()
    splash.overrideredirect(True)
    ancho_ventana = 500
    alto_ventana = 700

    ancho_pantalla = splash.winfo_screenwidth()
    alto_pantalla = splash.winfo_screenheight()
    x = (ancho_pantalla // 2) - (ancho_ventana // 2)
    y = (alto_pantalla // 2) - (alto_ventana // 2)
    splash.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

    splash.configure(fg_color="black")
    splash.attributes("-alpha", 0.0)

    frame = ctk.CTkFrame(splash, corner_radius=50, fg_color="black")
    frame.pack(expand=True, fill="both", padx=10, pady=10)

    imagen_logo = Image.open(os.path.join(CARPETA_RECURSOS, "logo.png"))
    imagen_by = Image.open(os.path.join(CARPETA_RECURSOS, "by.png"))
    imagen_estudio = Image.open(os.path.join(CARPETA_RECURSOS, "myfirstchamba.png"))

    ctk.CTkLabel(frame, image=ctk.CTkImage(imagen_logo, size=(600, 400)), text="").pack(pady=(10, 5))
    ctk.CTkLabel(frame, image=ctk.CTkImage(imagen_by, size=(80, 35)), text="").pack(pady=(0, 3))
    ctk.CTkLabel(frame, image=ctk.CTkImage(imagen_estudio, size=(400, 250)), text="").pack(pady=(0, 5))

    def fade_in(opacidad=0.0):
        if opacidad < 1.0:
            splash.attributes("-alpha", opacidad)
            splash.after(50, lambda: fade_in(opacidad + 0.05))
        else:
            splash.after(3000, lambda: fade_out(1.0))

    def fade_out(opacidad):
        if opacidad > 0:
            splash.attributes("-alpha", opacidad)
            splash.after(50, lambda: fade_out(opacidad - 0.05))
        else:
            splash.destroy()
            callback_despues()

    fade_in()
    splash.mainloop()
