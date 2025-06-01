import sys
import os
import json
from .game.main_game import HexGame
from .game.game_state import GameState

SAVES_DIR = os.path.join(os.path.dirname(__file__), "saves")


def save_game_state(usuario, game_state):
    os.makedirs(SAVES_DIR, exist_ok=True)
    save_path = os.path.join(SAVES_DIR, f"{usuario}.hexalink.json")
    try:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(game_state.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"[GUARDADO] Partida guardada para {usuario} en {save_path}")
    except Exception as e:
        print(f"[ERROR] No se pudo guardar la partida: {e}")


def load_game_state(usuario):
    save_path = os.path.join(SAVES_DIR, f"{usuario}.hexalink.json")
    if not os.path.exists(save_path):
        print(f"[INFO] No existe partida guardada para {usuario}.")
        return None
    try:
        with open(save_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return GameState.from_dict(data)
    except Exception as e:
        print(f"[ERROR] No se pudo cargar la partida: {e}")
        return None


def iniciar_hexalink(usuario, cargar=False):
    game_state = None
    if cargar:
        try:
            game_state = load_game_state(usuario)
            if not game_state:
                pass  # No se pudo cargar la partida, se iniciará una nueva.
        except Exception:
            game_state = None

    try:
        if game_state:
            game = HexGame(usuario=usuario, game_state=game_state)
        else:
            game = HexGame(usuario=usuario)
    except Exception:
        return  # No cerrar el programa abruptamente

    # Hook para guardar al salir
    original_run = game.run

    def run_and_save():
        original_run()
        save_game_state(usuario, game.game_state)

    game.run = run_and_save
    game.run()


if __name__ == "__main__":
    usuario = sys.argv[1] if len(sys.argv) > 1 else "default"
    cargar = sys.argv[2] == "cargar" if len(sys.argv) > 2 else False
    iniciar_hexalink(usuario, cargar=cargar)