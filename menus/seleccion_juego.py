import customtkinter as ctk
from PIL import Image
import os
import subprocess

class MenuSeleccionJuego:
    def __init__(self, usuario):
        self.usuario = usuario
        self.root = ctk.CTk()
        self.root.title("Seleccionar Juego")
        self.root.geometry("500x550")
        self.root.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.construir_interfaz()
        self.root.mainloop()

    def construir_interfaz(self):
        ctk.CTkLabel(self.root, text="Selecciona un juego", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        # Imagen del juego Hexa-Link
        imagen_path = os.path.join("recursos", "hexalink.jpg")
        imagen = ctk.CTkImage(dark_image=Image.open(imagen_path), size=(200, 200))
        ctk.CTkLabel(self.root, image=imagen, text="").pack(pady=10)

        ctk.CTkButton(self.root, text="Jugar Hexa-Link", command=self.abrir_hexalink).pack(pady=10)
        ctk.CTkButton(self.root, text="Jugar Lexicograma (próximamente)", state="disabled").pack(pady=10)
        ctk.CTkButton(self.root, text="Salir", fg_color="red", hover_color="darkred", command=self.root.destroy).pack(pady=20)

    def abrir_hexalink(self):
        ruta_hexalink = os.path.join("Hexa_Link", "hexalink.py")
        subprocess.run(["python", ruta_hexalink, self.usuario])


def iniciar_menu(usuario):
    MenuSeleccionJuego(usuario)
