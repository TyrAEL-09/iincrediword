import customtkinter as ctk
from PIL import Image
import os
from auth.interfaz_login.autenticacion import iniciar_sesion
from auth.registro import ventana_registro

CARPETA_RECURSOS = "recursos" # Variable para cambiar el path de la imagen

def mostrar_formulario(root, mostrar_login_callback):
    imagen_logo = Image.open(os.path.join(CARPETA_RECURSOS, "logo.png"))
    logo = ctk.CTkImage(imagen_logo, size=(250, 250))
    
    ctk.CTkLabel( # Muestra el logo de IINcrediWord
        root,
        image=logo, text=""
    ).grid(row=0, column=0, pady=(10, 5))

    ctk.CTkLabel( # Muestra texto
        root,
        text="Inicio de Sesión a MyFirstChamba-Hub",
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color="#00BFFF"
    ).grid(row=1, column=0, pady=5),

    entry_email = ctk.CTkEntry( # Recibe el email
        root,
        placeholder_text="Email",
        height=24, font=ctk.CTkFont(size=13)
    )
    entry_email.grid(row=2, column=0, padx=80, pady=(0, 10), sticky="nsew")

    entry_password = ctk.CTkEntry( # Recibe la password
        root, 
        placeholder_text="Contraseña", 
        show="*", 
        height=24, 
        font=ctk.CTkFont(size=13)
    )
    entry_password.grid(row=3, column=0, padx=80, pady=(0, 10), sticky="nsew")

    ctk.CTkButton(  # Botón de Iniciar Sesión
        root, 
        text="Iniciar sesión",
        height=28,
        font=ctk.CTkFont(size=13),
        command=lambda: iniciar_sesion(entry_email, entry_password, root)
    ).grid(row=4, column=0, pady=(0, 10))

    ctk.CTkLabel( #Muestra texto
        root, 
        text="¿No tienes cuenta?",
        font=ctk.CTkFont(size=12)
    ).grid(row=5, column=0)
    
    ctk.CTkButton( # Botón de Registrarse
        root,
        text="Registrarse",
        height=26, font=ctk.CTkFont(size=12),
        command=lambda: [root.destroy(), ventana_registro(mostrar_login_callback)], fg_color="gray"
    ).grid(row=6, column=0, pady=(0, 20))