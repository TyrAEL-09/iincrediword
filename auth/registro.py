import customtkinter as ctk
from .registro_ui import crear_interfaz_registro
from .registro_logic import validar_y_registrar

def ventana_registro(ventana_login_func):
    ventana = ctk.CTk()

    entry_email, entry_pass, entry_conf, boton_registrar = crear_interfaz_registro(ventana, ventana_login_func)

    def registrar():
        email = entry_email.get().strip()
        password = entry_pass.get().strip()
        confirmar = entry_conf.get().strip()
        validar_y_registrar(email, password, confirmar, ventana, ventana_login_func)

    boton_registrar.configure(command=registrar)

    ventana.mainloop()
