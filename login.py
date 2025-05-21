import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os

# Rutas de carpetas
CARPETA_DATOS = "datos"
CARPETA_RECURSOS = "recursos"
ARCHIVO_USUARIOS = os.path.join(CARPETA_DATOS, "usuarios.txt")

# Configuraciones globales
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# ---------------- FUNCIONES BÁSICAS ---------------- #

def asegurar_estructura_directorios():
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    os.makedirs(CARPETA_RECURSOS, exist_ok=True)

def cargar_usuarios():
    usuarios = {}
    try:
        with open(ARCHIVO_USUARIOS, "r") as archivo:
            for linea in archivo:
                email, password = linea.strip().split(":")
                usuarios[email] = password
    except FileNotFoundError:
        pass
    return usuarios

# ---------------- FUNCIONES PRINCIPALES ---------------- #

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
            # Aquí puedes continuar a la siguiente parte del programa (selección de juegos)
        else:
            messagebox.showerror("Error", "Contraseña incorrecta.")
    else:
        messagebox.showwarning("No registrado", "El email no está registrado. Por favor regístrate.")

def abrir_ventana_registro():
    ventana = ctk.CTk()
    ventana.title("Registro")
    ventana.geometry("600x500")
    ventana.minsize(400, 400)

    for i in range(10):
        ventana.rowconfigure(i, weight=1)
    ventana.columnconfigure(0, weight=1)

    ctk.CTkLabel(ventana, text="Registro de Usuario", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=5)

    entry_email_r = ctk.CTkEntry(ventana, placeholder_text="Email", height=24, font=ctk.CTkFont(size=13))
    entry_email_r.grid(row=2, column=0, padx=80, pady=(0, 10), sticky="nsew")

    entry_pass_r = ctk.CTkEntry(ventana, placeholder_text="Contraseña", show="*", height=24, font=ctk.CTkFont(size=13))
    entry_pass_r.grid(row=3, column=0, padx=80, pady=(0, 10), sticky="nsew")

    entry_conf_r = ctk.CTkEntry(ventana, placeholder_text="Confirmar contraseña", show="*", height=24, font=ctk.CTkFont(size=13))
    entry_conf_r.grid(row=4, column=0, padx=80, pady=(0, 10), sticky="nsew")

    def registrar():
        email = entry_email_r.get().strip()
        password = entry_pass_r.get().strip()
        confirmar = entry_conf_r.get().strip()
        usuarios = cargar_usuarios()

        if not email or not password or not confirmar:
            messagebox.showerror("Error", "Completa todos los campos.")
        elif email in usuarios:
            messagebox.showerror("Error", "El email ya está registrado.")
        elif password != confirmar:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
        elif len(password) < 4:
            messagebox.showerror("Error", "La contraseña debe tener al menos 4 caracteres.")
        else:
            with open(ARCHIVO_USUARIOS, "a") as archivo:
                archivo.write(f"{email}:{password}\n")
            messagebox.showinfo("Éxito", "Usuario registrado exitosamente.")
            ventana.destroy()
            mostrar_login()

    ctk.CTkButton(ventana, text="Registrar", height=28, font=ctk.CTkFont(size=13), command=registrar).grid(row=5, column=0, pady=(10, 20))

    ventana.mainloop()

def mostrar_login():
    global root, entry_email, entry_password

    root = ctk.CTk()
    root.title("Iniciar Sesión en MyFirstChamba-Hub")
    root.geometry("700x500")
    root.minsize(400, 350)

    for i in range(10):
        root.rowconfigure(i, weight=1)
    root.columnconfigure(0, weight=1)

    imagen_original = Image.open(os.path.join(CARPETA_RECURSOS, "logo.png"))
    imagen = ctk.CTkImage(light_image=imagen_original, dark_image=imagen_original, size=(420, 270))
    ctk.CTkLabel(root, image=imagen, text="").grid(row=0, column=0, pady=(10, 5))

    ctk.CTkLabel(root, text="Inicio de Sesión a MyFirstChamba-Hub", font=ctk.CTkFont(size=20, weight="bold")).grid(row=1, column=0, pady=5)

    entry_email = ctk.CTkEntry(root, placeholder_text="Email", height=24, font=ctk.CTkFont(size=13))
    entry_email.grid(row=2, column=0, padx=80, pady=(0, 10), sticky="nsew")

    entry_password = ctk.CTkEntry(root, placeholder_text="Contraseña", show="*", height=24, font=ctk.CTkFont(size=13))
    entry_password.grid(row=3, column=0, padx=80, pady=(0, 10), sticky="nsew")

    ctk.CTkButton(root, text="Iniciar sesión", height=28, font=ctk.CTkFont(size=13), command=iniciar_sesion).grid(row=4, column=0, pady=(0, 10))

    ctk.CTkLabel(root, text="¿No tienes cuenta?", font=ctk.CTkFont(size=12)).grid(row=5, column=0)
    ctk.CTkButton(root, text="Registrarse", height=26, font=ctk.CTkFont(size=12), command=lambda: [root.destroy(), abrir_ventana_registro()], fg_color="gray").grid(row=6, column=0, pady=(0, 20))

    root.mainloop()

def mostrar_splash():
    splash = ctk.CTk()
    splash.overrideredirect(True)
    splash.geometry("500x700")
    splash.configure(fg_color="black")
    splash.attributes("-alpha", 0.0)

    frame = ctk.CTkFrame(splash, corner_radius=50, fg_color="black")
    frame.pack(expand=True, fill="both", padx=10, pady=10)

    imagen_logo = Image.open(os.path.join(CARPETA_RECURSOS, "logo.png"))
    imagen_by = Image.open(os.path.join(CARPETA_RECURSOS, "by.png"))
    imagen_estudio = Image.open(os.path.join(CARPETA_RECURSOS, "myfirstchamba.png"))

    label_logo = ctk.CTkLabel(frame, image=ctk.CTkImage(imagen_logo, size=(600, 400)), text="")
    label_logo.pack(pady=(10, 5))

    label_by = ctk.CTkLabel(frame, image=ctk.CTkImage(imagen_by, size=(80, 35)), text="")
    label_by.pack(pady=(0, 3))

    label_estudio = ctk.CTkLabel(frame, image=ctk.CTkImage(imagen_estudio, size=(400, 250)), text="")
    label_estudio.pack(pady=(0, 5))

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
            mostrar_login()

    fade_in()
    splash.mainloop()

# ---------------- INICIALIZACIÓN ---------------- #

def iniciar_aplicacion():
    asegurar_estructura_directorios()
    mostrar_splash()

if __name__ == "__main__":
    iniciar_aplicacion()
