# Hexa_Link/partida.py

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from constants import HEXA_LINK_SAVE_FILE

def _parse_estado(lineas):
    estado = {}
    for linea in lineas:
        if ':' not in linea:
            continue
        clave, valor = linea.split(':', 1)
        clave = clave.strip()
        valor = valor.strip()
        if clave == "palabras_objetivo" or clave == "encontradas":
            estado[clave] = valor.split(',') if valor else []
        elif clave == "letras":
            estado[clave] = valor.split(',') if valor else []
        elif clave == "central":
            estado[clave] = valor
        elif clave == "tiempo":
            estado[clave] = int(valor)
    return estado

def cargar_partida_guardada(usuario):
    if not os.path.exists(HEXA_LINK_SAVE_FILE):
        return None
    with open(HEXA_LINK_SAVE_FILE, "r", encoding="utf-8") as f:
        contenido = f.read()

    bloques = contenido.split('\n\n')
    for bloque in bloques:
        lineas = bloque.strip().splitlines()
        if not lineas:
            continue
        if lineas[0].strip() == f"#{usuario}":
            return _parse_estado(lineas[1:])
    return None

def guardar_partida(usuario, estado):
    # Leer todo
    bloques = []
    if os.path.exists(HEXA_LINK_SAVE_FILE):
        with open(HEXA_LINK_SAVE_FILE, "r", encoding="utf-8") as f:
            contenido = f.read()
        bloques = contenido.split('\n\n')

    nuevo_bloque = [f"#{usuario}"]
    nuevo_bloque.append("palabras_objetivo: " + ",".join(estado.get("palabras_objetivo", [])))
    nuevo_bloque.append("letras: " + ",".join(estado.get("letras", [])))
    nuevo_bloque.append("central: " + estado.get("central", ""))
    nuevo_bloque.append("encontradas: " + ",".join(estado.get("encontradas", [])))
    nuevo_bloque.append("tiempo: " + str(estado.get("tiempo", 0)))

    # Reemplazar bloque si existe
    encontrado = False
    for i, bloque in enumerate(bloques):
        lineas = bloque.strip().splitlines()
        if lineas and lineas[0].strip() == f"#{usuario}":
            bloques[i] = "\n".join(nuevo_bloque)
            encontrado = True
            break
    if not encontrado:
        bloques.append("\n".join(nuevo_bloque))

    with open(HEXA_LINK_SAVE_FILE, "w", encoding="utf-8") as f:
        f.write("\n\n".join(bloques))