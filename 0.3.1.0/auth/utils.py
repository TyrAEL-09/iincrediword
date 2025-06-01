import os

CARPETA_DATOS = "datos"
ARCHIVO_USUARIOS = os.path.join(CARPETA_DATOS, "usuarios.txt")

def asegurar_estructura_directorios():
    os.makedirs(CARPETA_DATOS, exist_ok=True)

def cargar_usuarios():
    usuarios = {}
    try:
        with open(ARCHIVO_USUARIOS, "r") as archivo:
            for linea in archivo:
                if ":" in linea:
                    partes = linea.strip().split(":", 1)
                    if len(partes) == 2:
                        email, password = partes
                        usuarios[email] = password
    except FileNotFoundError:
        pass
    return usuarios

def registrar_usuario(email: str, password: str):
    with open(ARCHIVO_USUARIOS, "a") as archivo:
        archivo.write(f"{email}:{password}\n")