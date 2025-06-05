import os
import random
from Hexa_Link.game.constants import WORDS_FILE
from collections import Counter

def cargar_pals(path=None):
    if path is None:
        path = WORDS_FILE
    with open(path, "r", encoding="utf-8") as f:
        return [w.strip().strip('"').lower() for w in f if w.strip()]

def elegir():
    palabras_completo = cargar_pals()
    # Buscar palabras que usen SOLO las 7 letras (con posibles repeticiones) y contengan todas
    heptacracks = [w for w in palabras_completo if len(w) >= 7 and set(w) == set(w) and len(set(w)) == 7]
    random.shuffle(heptacracks)
    for heptacrack in palabras_completo:
        unique_letras = set(heptacrack)
        if len(heptacrack) >= 7 and len(unique_letras) == 7:
            pool = list(unique_letras)
            center = random.choice(pool)
            # Palabras válidas: usan solo letras del pool
            valid = list({
                w for w in palabras_completo
                if center in w and len(w) >= 3 and set(w) <= unique_letras
            })
            # El heptacrack debe ser la única palabra válida que use todas las 7 letras (con repeticiones permitidas)
            heptacracks_in_valid = [w for w in valid if set(w) == unique_letras and all(w.count(l) >= 1 for l in unique_letras) and len(w) >= 7]
            if len(heptacracks_in_valid) == 1 and 50 <= len(valid) <= 100:
                print(f"Palabras válidas ({len(valid)}): {valid}")
                return pool, center, valid
    # Fallback: lógica anterior
    while True:
        pool = random.sample(list("abcdefghijklmnopqrstuvwxyz"), 7)
        center = random.choice(pool)
        valid = list({
            w for w in palabras_completo
            if center in w and len(w) >= 3 and set(w) <= set(pool)
        })
        if 50 <= len(valid) <= 100:
            print(f"Palabras válidas ({len(valid)}): {valid}")
            return pool, center, valid