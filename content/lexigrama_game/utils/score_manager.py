# score_manager.py
import json
import os
from pathlib import Path

class ScoreManager:
    BEST_SCORES_FILE = str(Path(__file__).resolve().parent.parent / "mejores_puntajes.json")
    MAX_SCORES = 10

    @staticmethod
    def load_scores() -> list:
        """Loads scores from the JSON file."""
        if not os.path.exists(ScoreManager.BEST_SCORES_FILE):
            return []
        try:
            with open(ScoreManager.BEST_SCORES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("top_scores", [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def save_score(username: str, score: int, time_elapsed: int):
        """
        Guarda el mejor puntaje y menor tiempo por usuario en la leaderboard.
        Si el usuario ya existe, solo se actualiza si el nuevo puntaje es mayor,
        o si el puntaje es igual y el tiempo es menor.
        """
        try:
            if not os.path.exists(ScoreManager.BEST_SCORES_FILE):
                data_to_save = {"top_scores": []}
            else:
                with open(ScoreManager.BEST_SCORES_FILE, "r", encoding="utf-8") as f:
                    data_to_save = json.load(f)
                    if "top_scores" not in data_to_save:
                        data_to_save = {"top_scores": []}

            scores = data_to_save["top_scores"]
            new_score = {"nombre": username, "puntaje": score, "tiempo": time_elapsed}
            
            # Buscar si el usuario ya existe
            user_found = False
            for entry in scores:
                if entry["nombre"] == username:
                    user_found = True
                    if score > entry["puntaje"] or (score == entry["puntaje"] and time_elapsed < entry["tiempo"]):
                        entry.update(new_score)
                    break
            
            # Si el usuario no existe, agregar el nuevo puntaje
            if not user_found:
                scores.append(new_score)
            
            # Ordenar por puntaje descendente y tiempo ascendente
            scores.sort(key=lambda x: (-x["puntaje"], x["tiempo"]))
            
            # Mantener solo los top 10
            data_to_save["top_scores"] = scores[:10]
            
            # Guardar el archivo
            with open(ScoreManager.BEST_SCORES_FILE, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, indent=4, ensure_ascii=False)
                
            print(f"Puntaje guardado exitosamente: {username} - {score} pts - {time_elapsed}s")
            return True
        except Exception as e:
            print(f"Error al guardar puntaje: {e}")
            return False

    @staticmethod
    def get_top_scores() -> list:
        """Returns the sorted list of top scores."""
        scores = ScoreManager.load_scores()
        scores.sort(key=lambda x: (-x.get('puntaje', 0), x.get('tiempo', 0)))
        return scores[:ScoreManager.MAX_SCORES]

    @staticmethod
    def update_best_scores_from_saves():
        """
        Lee partidas_guardadas.json y actualiza mejores_puntajes.json
        con los mejores puntajes y menor tiempo por usuario.
        """
        base_dir = Path(__file__).resolve().parent.parent
        saves_path = base_dir / "saves" / "partidas_guardadas.json"
        best_scores_path = base_dir / "mejores_puntajes.json"

        if not saves_path.exists():
            print(f"No existe {saves_path}")
            return

        try:
            with open(saves_path, "r", encoding="utf-8") as f:
                saves = json.load(f)
        except Exception as e:
            print(f"Error leyendo {saves_path}: {e}")
            return

        best_by_user = {}
        for username, data in saves.items():
            score = data.get("score", 0)
            time_elapsed = data.get("time_elapsed", 0)
            if username not in best_by_user:
                best_by_user[username] = {"puntaje": score, "tiempo": time_elapsed}
            else:
                prev = best_by_user[username]
                if score > prev["puntaje"] or (score == prev["puntaje"] and time_elapsed < prev["tiempo"]):
                    best_by_user[username] = {"puntaje": score, "tiempo": time_elapsed}

        best_scores = [
            {"nombre": user, "puntaje": info["puntaje"], "tiempo": info["tiempo"]}
            for user, info in best_by_user.items()
        ]
        best_scores.sort(key=lambda x: (-x["puntaje"], x["tiempo"]))
        data_to_save = {"top_scores": best_scores[:10]}
        with open(best_scores_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=4, ensure_ascii=False)