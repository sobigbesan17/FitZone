import sqlite3
import pandas as pd


class GymWorkoutRecommendationAlgorithm:
    def __init__(self, db_file="FitZone.db"):
        self.conn = sqlite3.connect(db_file)
        self.data = None

    def load_data(self):
        query = """
            SELECT WorkoutName, WorkoutType, WorkoutGoal, Description,
                Difficulty, ImagePath, Equipment, WarmupDuration, CooldownDuration
            FROM Workouts
        """
        self.data = pd.read_sql_query(query, self.conn)
        if self.data is not None:
            self.data.fillna("", inplace=True)
            self.data["WorkoutType"] = self.data["WorkoutType"].astype(str)
            self.data["WorkoutGoal"] = self.data["WorkoutGoal"].astype(str)
            self.data["Difficulty"] = self.data["Difficulty"].astype(str)
            self.data["Equipment"] = self.data["Equipment"].astype(str)
            numeric_columns = ["WarmupDuration", "CooldownDuration"]
            for col in numeric_columns:
                if col in self.data.columns:
                    self.data[col] = pd.to_numeric(self.data[col], errors="coerce").fillna(0)

    def preprocess_data(self):
        # No machine learning model required; just normalize the dataset.
        if self.data is None or self.data.empty:
            return
        self.data["Ingredients_set"] = self.data["Equipment"].apply(self._token_set)

    def get_recommendation(self, user_input):
        if self.data is None or self.data.empty:
            return "No workout data available."

        normalized_input = self._normalize_input(user_input)
        candidates = self.data.copy()

        def score_row(row):
            score = 0.0
            if normalized_input["WorkoutType"] and normalized_input["WorkoutType"] != "none":
                score += 0 if row["WorkoutType"].strip().lower() == normalized_input["WorkoutType"] else 5
            if normalized_input["WorkoutGoal"] and normalized_input["WorkoutGoal"] != "none":
                score += 0 if row["WorkoutGoal"].strip().lower() == normalized_input["WorkoutGoal"] else 5
            if normalized_input["Difficulty"] and normalized_input["Difficulty"] != "none":
                score += 0 if row["Difficulty"].strip().lower() == normalized_input["Difficulty"] else 3

            similarity = self._token_similarity(normalized_input["Equipment"], row["Equipment"])
            score += (1 - similarity) * 10

            score += abs(row.get("WarmupDuration", 0) - normalized_input["WarmupDuration"])
            score += abs(row.get("CooldownDuration", 0) - normalized_input["CooldownDuration"])
            return score

        candidates["match_score"] = candidates.apply(score_row, axis=1)
        best = candidates.sort_values(by="match_score").iloc[0]
        return f"Recommended Workout: {best['WorkoutName']}"

    def _normalize_input(self, user_input):
        normalized = {
            "WorkoutType": str(user_input.get("WorkoutType", "")).strip().lower(),
            "WorkoutGoal": str(user_input.get("WorkoutGoal", "")).strip().lower(),
            "Difficulty": str(user_input.get("Difficulty", "")).strip().lower(),
            "Equipment": str(user_input.get("Equipment", "")).strip().lower(),
            "WarmupDuration": self._safe_float(user_input.get("WarmupDuration", 0)),
            "CooldownDuration": self._safe_float(user_input.get("CooldownDuration", 0)),
        }
        return normalized

    def _token_set(self, text):
        return {token.strip().lower() for token in str(text).split(",") if token.strip()}

    def _token_similarity(self, text_a, text_b):
        set_a = self._token_set(text_a)
        set_b = self._token_set(text_b)
        if not set_a or not set_b:
            return 0.0
        intersect = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        return intersect / union if union else 0.0

    def _safe_float(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0


if __name__ == "__main__":
    user_input = {
        "WorkoutType": "Swimming",
        "WorkoutGoal": "Weight Loss",
        "Difficulty": "Advanced",
        "Equipment": "Swimsuit",
        "WarmupDuration": 5,
        "CooldownDuration": 5,
    }
    recommendation_algorithm = GymWorkoutRecommendationAlgorithm()
    recommendation_algorithm.load_data()
    recommendation_algorithm.preprocess_data()
    recommended_workout = recommendation_algorithm.get_recommendation(user_input)
    print(recommended_workout)
