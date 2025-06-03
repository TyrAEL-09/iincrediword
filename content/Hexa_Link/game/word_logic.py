import os
import random
from Hexa_Link.game.constants import WORDS_FILE
from collections import Counter

def load_words(path=None):
    if path is None:
        path = WORDS_FILE
    with open(path, "r", encoding="utf-8") as f:
        return [w.strip().strip('"').lower() for w in f if w.strip()]

def choose_letters_and_words():
    all_words = load_words()
    # Buscar palabras que usen SOLO las 7 letras (con posibles repeticiones) y contengan todas
    heptacracks = [w for w in all_words if len(w) >= 7 and set(w) == set(w) and len(set(w)) == 7]
    random.shuffle(heptacracks)
    for heptacrack in all_words:
        unique_letters = set(heptacrack)
        if len(heptacrack) >= 7 and len(unique_letters) == 7:
            pool = list(unique_letters)
            center = random.choice(pool)
            # Palabras válidas: usan solo letras del pool
            valid = list({
                w for w in all_words
                if center in w and len(w) >= 3 and set(w) <= unique_letters
            })
            # El heptacrack debe ser la única palabra válida que use todas las 7 letras (con repeticiones permitidas)
            heptacracks_in_valid = [w for w in valid if set(w) == unique_letters and all(w.count(l) >= 1 for l in unique_letters) and len(w) >= 7]
            if len(heptacracks_in_valid) == 1 and 50 <= len(valid) <= 100:
                print(f"Palabras válidas ({len(valid)}): {valid}")
                return pool, center, valid
    # Fallback: lógica anterior
    while True:
        pool = random.sample(list("abcdefghijklmnopqrstuvwxyz"), 7)
        center = random.choice(pool)
        valid = list({
            w for w in all_words
            if center in w and len(w) >= 3 and set(w) <= set(pool)
        })
        if 50 <= len(valid) <= 100:
            print(f"Palabras válidas ({len(valid)}): {valid}")
            return pool, center, valid