import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
from auth.utils import cargar_usuarios
from auth.registro import ventana_registro
from menus import seleccion_juego

CARPETA_RECURSOS = "recursos"

def crear_formulario(root, mostrar_login_callback):
    imagen_logo = Image.open(os.path.join(CARPETA_RECURSOS, "logo.png"))
    logo = ctk.CTkImage(imagen_logo, size=(420, 270))
    ctk.CTkLabel(root, image=logo, text="").grid(row=0, column=0, pady=(10, 5))

    ctk.CTkLabel(root, text="Inicio de Sesión a MyFirstChamba-Hub", font=ctk.CTkFont(size=20, weight="bold")).grid(row=1, column=0, pady=5)

    entry_email = ctk.CTkEntry(root, placeholder_text="Email", height=24, font=ctk.CTkFont(size=13))
    entry_email.grid(row=2, column=0, padx=80, pady=(0, 10), sticky="nsew")

    entry_password = ctk.CTkEntry(root, placeholder_text="Contraseña", show="*", height=24, font=ctk.CTkFont(size=13))
    entry_password.grid(row=3, column=0, padx=80, pady=(0, 10), sticky="nsew")

    def iniciar_sesion():
        email = entry_email.get().strip()
        password = entry_password.get().strip()
        usuarios = cargar_usuarios()

        if not email or not password:
            messagebox.showerror("Error", "Completa todos los campos.")
        elif email in usuarios:
            if usuarios[email] == password:
                messagebox.showinfo("Éxito", f"Bienvenido {email}")
                root.destroy()
                seleccion_juego.iniciar_menu(email)
            else:
                messagebox.showerror("Error", "Contraseña incorrecta.")
        else:
            messagebox.showwarning("No registrado", "El email no está registrado. Por favor regístrate.")

    ctk.CTkButton(root, text="Iniciar sesión", height=28, font=ctk.CTkFont(size=13), command=iniciar_sesion).grid(row=4, column=0, pady=(0, 10))

    ctk.CTkLabel(root, text="¿No tienes cuenta?", font=ctk.CTkFont(size=12)).grid(row=5, column=0)
    ctk.CTkButton(root, text="Registrarse", height=26, font=ctk.CTkFont(size=12), command=lambda: [root.destroy(), ventana_registro(mostrar_login_callback)], fg_color="gray").grid(row=6, column=0, pady=(0, 20))
