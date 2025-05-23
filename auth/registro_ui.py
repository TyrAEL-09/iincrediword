import customtkinter as ctk

def crear_interfaz_registro(ventana, ventana_login_func):
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    ventana.title("Registro - MyFirstChamba")
    ventana.geometry("480x550")
    ventana.minsize(420, 450)
    ventana.eval('tk::PlaceWindow . center')

    fondo = ctk.CTkFrame(ventana, fg_color="#0f1219")
    fondo.pack(expand=True, fill="both")

    frame_principal = ctk.CTkFrame(fondo, corner_radius=20, fg_color="#1c2233")
    frame_principal.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.85)

    titulo = ctk.CTkLabel(frame_principal, text="Crear Nueva Cuenta", font=ctk.CTkFont(size=24, weight="bold"))
    titulo.pack(pady=(25, 30))

    etiqueta_email = ctk.CTkLabel(frame_principal, text="Email", font=ctk.CTkFont(size=14))
    etiqueta_email.pack(anchor="w", padx=30)
    entry_email = ctk.CTkEntry(frame_principal, placeholder_text="ejemplo@correo.com", height=32, font=ctk.CTkFont(size=14))
    entry_email.pack(fill="x", padx=30, pady=(0, 20))

    etiqueta_pass = ctk.CTkLabel(frame_principal, text="Contraseña", font=ctk.CTkFont(size=14))
    etiqueta_pass.pack(anchor="w", padx=30)
    entry_pass = ctk.CTkEntry(frame_principal, placeholder_text="********", show="*", height=32, font=ctk.CTkFont(size=14))
    entry_pass.pack(fill="x", padx=30, pady=(0, 20))

    etiqueta_conf = ctk.CTkLabel(frame_principal, text="Confirmar Contraseña", font=ctk.CTkFont(size=14))
    etiqueta_conf.pack(anchor="w", padx=30)
    entry_conf = ctk.CTkEntry(frame_principal, placeholder_text="********", show="*", height=32, font=ctk.CTkFont(size=14))
    entry_conf.pack(fill="x", padx=30, pady=(0, 30))

    boton_registrar = ctk.CTkButton(frame_principal, text="Registrar", height=45, font=ctk.CTkFont(size=16, weight="bold"),
                                    fg_color="#3399ff", hover_color="#1a73e8")
    boton_registrar.pack(fill="x", padx=50)

    boton_volver = ctk.CTkButton(frame_principal, text="← Volver al inicio de sesión", height=38,
                                 font=ctk.CTkFont(size=14), fg_color="#2d2f3a", hover_color="#454a5a",
                                 command=lambda: [ventana.destroy(), ventana_login_func()])
    boton_volver.pack(fill="x", padx=50, pady=(20, 10))

    return entry_email, entry_pass, entry_conf, boton_registrar
