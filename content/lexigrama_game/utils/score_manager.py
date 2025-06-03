# score_manager.py
import json
import os

class ScoreManager:
    """Handles loading, saving, and managing top scores."""

    SCORE_FILE = "best_scores.json"
    MAX_SCORES = 10

    @staticmethod
    def load_scores() -> list:
        """Loads scores from the JSON file."""
        if not os.path.exists(ScoreManager.SCORE_FILE):
            return []
        try:
            with open(ScoreManager.SCORE_FILE, "r") as f:
                data = json.load(f)
                return data.get("top_scores", [])
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is corrupted, return empty list
            return []

    @staticmethod
    def save_score(username: str, score: int, time_str: str):
        """
        Saves a new score, maintaining the top N scores.
        Scores are sorted by 'puntaje' (descending).
        """
        current_scores = ScoreManager.load_scores()

        new_score_entry = {
            "nombre": username,
            "puntaje": score,
            "tiempo": time_str
        }
        current_scores.append(new_score_entry)

        # Sort by score in descending order
        current_scores.sort(key=lambda x: x.get('puntaje', 0), reverse=True)

        # Keep only the top MAX_SCORES
        data_to_save = {"top_scores": current_scores[:ScoreManager.MAX_SCORES]}

        with open(ScoreManager.SCORE_FILE, "w") as f:
            json.dump(data_to_save, f, indent=4)
        print(f"Score saved for {username}: {score} in {time_str}. File: {ScoreManager.SCORE_FILE}")

    @staticmethod
    def get_top_scores() -> list:
        """Returns the sorted list of top scores."""
        scores = ScoreManager.load_scores()
        # Ensure they are sorted again in case manual edits or other issues
        scores.sort(key=lambda x: x.get('puntaje', 0), reverse=True)
        return scores[:ScoreManager.MAX_SCORES]