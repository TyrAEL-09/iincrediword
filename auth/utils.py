import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from constants import DATOS_DIR, USUARIOS_FILE

def asegurar_estructura_directorios():
    os.makedirs(DATOS_DIR, exist_ok=True)

def cargar_usuarios():
    usuarios = {}
    try:
        with open(USUARIOS_FILE, "r") as archivo:
            for linea in archivo:
                if ":" in linea:
                    email, password = linea.strip().split(":")
                    usuarios[email] = password
    except FileNotFoundError:
        pass
    return usuarios

def registrar_usuario(email: str, password: str):
    with open(USUARIOS_FILE, "a") as archivo:
        archivo.write(f"{email}:{password}\n")