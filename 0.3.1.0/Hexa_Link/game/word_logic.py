import os
import random
from Hexa_Link.game.constants import WORDS_FILE

def load_words(path=None):
    if path is None:
        path = WORDS_FILE
    with open(path, "r", encoding="utf-8") as f:
        return [w.strip().strip('"').lower() for w in f if w.strip()]

def choose_letters_and_words():
    while True:
        pool = random.sample(list("abcdefghijklmnopqrstuvwxyz"), 7)
        center = random.choice(pool)
        all_words = load_words()
        
        valid = list({
            w for w in all_words 
            if center in w and 
            len(w) >= 3 and 
            set(w) <= set(pool)
        })
        
        if 1 <= len(valid) <= 10:
            print(f"Palabras válidas ({len(valid)}): {valid}")
            return pool, center, valid