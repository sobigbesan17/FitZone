import sqlite3
import pandas as pd


class GymMealRecommendationAlgorithm:
    def __init__(self, db_file="FitZone.db"):
        self.conn = sqlite3.connect(db_file)
        self.data = None

    def load_data(self):
        query = """
            SELECT MealName, MealType, Calories, Protein, Fat, Carbohydrates,
                Ingredients, CookingTime, NutritionalGoals, Budget,
                DietaryRestrictions, Allergies, MealSize
            FROM Meals
            UNION ALL
            SELECT MealName, MealType, Calories, Protein, Fat, Carbohydrates,
                Ingredients, CookingTime, NutritionalGoals, Budget,
                DietaryRestrictions, Allergies, MealSize
            FROM CustomMeals
        """
        self.data = pd.read_sql_query(query, self.conn)
        if self.data is not None:
            self.data.fillna("", inplace=True)
            self.data["Ingredients"] = self.data["Ingredients"].astype(str)
            self.data["MealType"] = self.data["MealType"].astype(str)

    def preprocess_data(self):
        if self.data is None or self.data.empty:
            return
        self.data["Ingredients_set"] = self.data["Ingredients"].apply(self._ingredient_set)
        numeric_columns = ["Calories", "Protein", "Fat", "Carbohydrates", "CookingTime", "Budget", "MealSize"]
        for col in numeric_columns:
            if col in self.data.columns:
                self.data[col] = pd.to_numeric(self.data[col], errors="coerce").fillna(0)

    def get_recommendation(self, user_input):
        if self.data is None or self.data.empty:
            return "No meal data available."

        user_input = self._normalize_user_input(user_input)
        candidate_data = self.data
        meal_type = str(user_input.get("MealType", "")).strip().lower()
        if meal_type and meal_type != "none":
            candidate_data = candidate_data[candidate_data["MealType"].str.lower() == meal_type]

        if candidate_data.empty:
            candidate_data = self.data

        best_recommendation = None
        best_score = float("inf")

        for _, row in candidate_data.iterrows():
            score = self._score_meal(row, user_input)
            if score < best_score:
                best_score = score
                best_recommendation = row["MealName"]

        if best_recommendation is None:
            return "No meaningful recommendations found."

        return f"Recommended Meal: {best_recommendation}"

    def _normalize_user_input(self, user_input):
        normalized = user_input.copy()
        normalized["Ingredients"] = ",".join(str(user_input.get("Ingredients", "")).split(","))
        normalized["MealType"] = ",".join(str(user_input.get("MealType", "")).split(","))
        numeric_fields = ["Calories", "Protein", "Fat", "Carbohydrates", "CookingTime", "Budget", "MealSize"]
        for field in numeric_fields:
            try:
                normalized[field] = float(user_input.get(field, 0) or 0)
            except (TypeError, ValueError):
                normalized[field] = 0
        return normalized

    def _score_meal(self, row, user_input):
        numeric_weight = 1.0
        ingredient_weight = 5.0
        score = 0.0

        for factor in ["Calories", "Protein", "Fat", "Carbohydrates", "CookingTime", "Budget", "MealSize"]:
            row_value = self._safe_float(row.get(factor, 0))
            user_value = float(user_input.get(factor, 0))
            score += numeric_weight * abs(row_value - user_value)

        ingredients_score = 1.0 - self.calculate_ingredients_similarity(
            user_input.get("Ingredients", ""), row.get("Ingredients", "")
        )
        score += ingredient_weight * ingredients_score

        dietary_restrictions = str(row.get("DietaryRestrictions", "")).lower()
        requested_diet = str(user_input.get("DietaryRestrictions", "")).lower()
        if requested_diet and requested_diet != "none" and requested_diet not in dietary_restrictions:
            score += 50

        allergies = str(user_input.get("Allergies", "")).lower()
        meal_allergies = str(row.get("Allergies", "")).lower()
        if allergies and allergies != "none" and allergies in meal_allergies:
            score += 100

        return score

    def _ingredient_set(self, ingredients):
        return set(str(ingredients).lower().replace(" ", "").split(",")) if ingredients else set()

    def calculate_ingredients_similarity(self, input_ingredients, meal_ingredients):
        input_set = self._ingredient_set(input_ingredients)
        meal_set = self._ingredient_set(meal_ingredients)
        if not input_set or not meal_set:
            return 0.0
        intersection = len(input_set.intersection(meal_set))
        union = len(input_set.union(meal_set))
        return intersection / union if union > 0 else 0.0

    def _safe_float(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0


if __name__ == "__main__":
    user_input = {
        "MealType": "Dinner",
        "Calories": 350,
        "Protein": 15,
        "Fat": 10,
        "Carbohydrates": 50,
        "Ingredients": "Onion, Black beans, tomato",
        "CookingTime": 10,
        "NutritionalGoals": "None",
        "Budget": 15.0,
        "DietaryRestrictions": "None",
        "Allergies": "None",
        "MealSize": 1,
    }
    recommendation_algorithm = GymMealRecommendationAlgorithm()
    recommendation_algorithm.load_data()
    recommendation_algorithm.preprocess_data()
    recommended_meal_details = recommendation_algorithm.get_recommendation(user_input)
    print(recommended_meal_details)
