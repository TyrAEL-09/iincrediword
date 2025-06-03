# Módulo de autenticación de entrada de datos

from tkinter import messagebox
from auth.utils import cargar_usuarios
from menus import seleccion_juego

def iniciar_sesion(entry_email, entry_password, root):
    email = entry_email.get().strip()
    password = entry_password.get().strip()
    usuarios = cargar_usuarios()

    if not email or not password: # Si los campos están vacíos
        messagebox.showerror("Error", "Completa todos los campos.")
    elif email in usuarios: # Si User y Pass coinciden
        if usuarios[email] == password:
            root.destroy()
            seleccion_juego.iniciar_menu(email)
        else: # Si no hay coincidencia
            messagebox.showerror("Error", "Contraseña incorrecta.")
    else: # Si no existe el email en la DB
        messagebox.showwarning("No registrado", "El email no está registrado. Por favor regístrate.")
