import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
from auth.utils import cargar_usuarios, asegurar_estructura_directorios
from auth.registro import ventana_registro
from menus import seleccion_juego

CARPETA_RECURSOS = "recursos"

def mostrar_login():
    asegurar_estructura_directorios()

    root = ctk.CTk()
    root.title("Iniciar Sesión en MyFirstChamba-Hub")
    root.geometry("700x500")
    root.minsize(400, 350)
    root.configure(fg_color="black")
    root.attributes("-alpha", 0.0)

    for i in range(10):
        root.rowconfigure(i, weight=1)
    root.columnconfigure(0, weight=1)

    # Splash frame con imagen myfirstchamba
    splash_frame = ctk.CTkFrame(root, fg_color="black")
    splash_frame.grid(row=0, column=0, rowspan=10, sticky="nsew")

    imagen_estudio = Image.open(os.path.join(CARPETA_RECURSOS, "myfirstchamba.png"))
    splash_img = ctk.CTkImage(imagen_estudio, size=(400, 300))
    ctk.CTkLabel(splash_frame, image=splash_img, text="").pack(expand=True)

    def fade_in(opacidad=0.0):
        if opacidad < 1.0:
            root.attributes("-alpha", opacidad)
            root.after(50, lambda: fade_in(opacidad + 0.05))
        else:
            root.after(3000, lambda: fade_out(1.0))

    def fade_out(opacidad):
        if opacidad > 0:
            root.attributes("-alpha", opacidad)
            root.after(50, lambda: fade_out(opacidad - 0.05))
        else:
            splash_frame.destroy()
            mostrar_formulario()
            fade_in_formulario(0.0)

    def fade_in_formulario(opacidad):
        if opacidad <= 1.0:
            root.attributes("-alpha", opacidad)
            root.after(30, lambda: fade_in_formulario(opacidad + 0.05))

    def mostrar_formulario():
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
        ctk.CTkButton(root, text="Registrarse", height=26, font=ctk.CTkFont(size=12), command=lambda: [root.destroy(), ventana_registro(mostrar_login)], fg_color="gray").grid(row=6, column=0, pady=(0, 20))

    fade_in()
    root.mainloop()