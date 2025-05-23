from tkinter import messagebox
from auth.utils import cargar_usuarios
from menus import seleccion_juego

def iniciar_sesion(entry_email, entry_password, root):
    email = entry_email.get().strip()
    password = entry_password.get().strip()
    usuarios = cargar_usuarios()

    if not email or not password:
        messagebox.showerror("Error", "Completa todos los campos.")
    elif email in usuarios:
        if usuarios[email] == password:
            root.destroy()
            seleccion_juego.iniciar_menu(email)
        else:
            messagebox.showerror("Error", "Contraseña incorrecta.")
    else:
        messagebox.showwarning("No registrado", "El email no está registrado. Por favor regístrate.")
