from tkinter import messagebox
from auth.utils import cargar_usuarios, registrar_usuario

def validar_y_registrar(email, password, confirmar, ventana, ventana_login_func):
    usuarios = cargar_usuarios()

    if not email or not password or not confirmar:
        messagebox.showerror("Error", "Completa todos los campos.")
        return False
    elif email in usuarios:
        messagebox.showerror("Error", "El email ya está registrado.")
        return False
    elif password != confirmar:
        messagebox.showerror("Error", "Las contraseñas no coinciden.")
        return False
    elif len(password) < 4:
        messagebox.showerror("Error", "La contraseña debe tener al menos 4 caracteres.")
        return False
    else:
        registrar_usuario(email, password)
        messagebox.showinfo("Éxito", "Usuario registrado exitosamente.")
        ventana.destroy()
        ventana_login_func()
        return True
