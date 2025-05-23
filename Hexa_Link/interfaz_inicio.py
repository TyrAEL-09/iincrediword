# interfaz_usuario.py
import customtkinter as ctk
from Hexa_Link.hexalink import iniciar_hexalink
from Hexa_Link.partida import guardar_partida, cargar_partida_guardada
from Hexa_Link.gestor_palabras import generar_palabras_y_letras

def interfaz_inicio(usuario):
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.geometry("400x400")
    root.title("HexaLink - Menú Inicial")

    def cargar_partida():
        estado = cargar_partida_guardada(usuario)
        if estado:
            nuevo_estado = iniciar_hexalink(estado, usuario)
            if nuevo_estado:
                guardar_partida(usuario, nuevo_estado)
        else:
            print("No hay partida guardada")

    def nueva_partida():
        palabras, letras, central = generar_palabras_y_letras()
        estado = {
            "palabras_objetivo": palabras,
            "letras": letras,
            "central": central,
            "encontradas": [],
            "tiempo": 0
        }
        nuevo_estado = iniciar_hexalink(estado, usuario)
        if nuevo_estado:
            guardar_partida(usuario, nuevo_estado)

    def cerrar_sesion():
        root.destroy()
        import auth.login
        auth.login.mostrar_login()

    def salir():
        root.destroy()

    ctk.CTkLabel(root, text="Bienvenido a HexaLink", font=("Arial", 20)).pack(pady=20)

    ctk.CTkButton(root, text="Cargar Partida", command=cargar_partida).pack(pady=10)
    ctk.CTkButton(root, text="Nueva Partida", command=nueva_partida).pack(pady=10)
    ctk.CTkButton(root, text="Cerrar Sesión", command=cerrar_sesion).pack(pady=10)
    ctk.CTkButton(root, text="Salir", command=salir).pack(pady=10)

    root.mainloop()