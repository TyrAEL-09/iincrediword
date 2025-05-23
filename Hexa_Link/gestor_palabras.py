# Hexa_Link/gestor_palabras.py
import random
import os
from collections import Counter

def cargar_banco_palabras():
    ruta = os.path.join("recursos", "bancopalabras.txt")
    with open(ruta, "r", encoding="utf-8") as f:
        return [linea.strip().lower() for linea in f if len(linea.strip()) >= 3]

def generar_palabras_y_letras():
    banco = cargar_banco_palabras()
    palabras_elegidas = random.sample(banco, random.randint(90, 130))

    letras_totales = "".join(palabras_elegidas)
    contador = Counter(letras_totales)

    # Escoger letras que aparecen más de 1 vez para garantizar uso
    letras_validas = [l for l in contador if contador[l] > 1]

    # Si no hay suficientes, completar con letras de palabras
    if len(letras_validas) < 7:
        letras_validas = list(contador.keys())

    # Elegir solo 7 letras
    letras_validas = letras_validas[:7]

    # Letra central obligatoria, elegir aleatoriamente
    central = random.choice(letras_validas)

    return palabras_elegidas, letras_validas, central