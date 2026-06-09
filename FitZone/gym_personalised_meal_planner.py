import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
from gym_font import ManageFont
from gym_function_bank import MessageHandler
from gym_meal_recommendation_algorithm import GymMealRecommendationAlgorithm


class PersonalisedMealPlannerPage(GymBasePage):
    def __init__(self, member_id, fitness_dashboard_callback, calculate_bmi_callback,
                 bmi_visualisation_callback, gym_meal_planner_callback,
                 gym_workout_planner_callback, view_class_schedule_callback,
                 gym_class_booking_callback, gym_class_clashes_callback):
        super().__init__()
        self.title("FitZone - Personalised Meal Planner")
        self.geometry("1000x700")
        self.member_id = member_id

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)

        self.recommendation_engine = GymMealRecommendationAlgorithm()
        self.recommendation_engine.load_data()
        self.recommendation_engine.preprocess_data()

        self.configure(background="#f2f2f2")
        self.create_meal_planner_page()

    def create_meal_planner_page(self):
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        content = tk.Frame(scrollable_frame)
        content.pack(fill=tk.X, pady=20, padx=20)

        tk.Label(content, text="Personalised Meal Planner", font=self.manage_font.large_bold_heading_font).pack(anchor=tk.W)
        tk.Label(content, text="Enter your preferences to get personalised meal recommendations.",
                 font=self.manage_font.medium_letters_font).pack(anchor=tk.W, pady=(0, 20))

        form_frame = tk.Frame(content)
        form_frame.pack(fill=tk.X)

        fields = [
            ("Meal Type:", "meal_type", ["Breakfast", "Lunch", "Dinner", "Snack"]),
            ("Dietary Restrictions:", "dietary_restrictions", ["None", "Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free"]),
            ("Allergies:", "allergies", ["None", "Nuts", "Dairy", "Gluten", "Shellfish"]),
            ("Nutritional Goals:", "nutritional_goals", ["None", "Weight Loss", "Muscle Gain", "Maintenance", "Heart Health"]),
            ("Meal Size:", "meal_size", ["1", "2", "3", "4", "5"]),
        ]

        self.combo_vars = {}
        row = 0
        for label_text, key, values in fields:
            tk.Label(form_frame, text=label_text, font=self.manage_font.medium_bold_letters_font).grid(
                row=row, column=0, sticky=tk.W, padx=10, pady=5
            )
            var = tk.StringVar(value=values[0])
            self.combo_vars[key] = var
            combo = ttk.Combobox(
                form_frame,
                textvariable=var,
                values=values,
                state="readonly",
                width=40,
                font=self.manage_font.medium_letters_font,
            )
            combo.grid(row=row, column=1, padx=10, pady=5)
            row += 1

        numeric_fields = [
            ("Calories (kcal):", "calories"),
            ("Protein (g):", "protein"),
            ("Fat (g):", "fat"),
            ("Carbohydrates (g):", "carbohydrates"),
            ("Cooking Time (min):", "cooking_time"),
            ("Budget ($):", "budget"),
        ]

        self.entry_vars = {}
        for label_text, key in numeric_fields:
            tk.Label(form_frame, text=label_text, font=self.manage_font.medium_bold_letters_font).grid(
                row=row, column=0, sticky=tk.W, padx=10, pady=5
            )
            var = tk.StringVar(value="0")
            self.entry_vars[key] = var
            entry = ttk.Entry(form_frame, textvariable=var, width=42, font=self.manage_font.medium_letters_font)
            entry.grid(row=row, column=1, padx=10, pady=5)
            row += 1

        tk.Label(form_frame, text="Ingredients:", font=self.manage_font.medium_bold_letters_font).grid(
            row=row, column=0, sticky=tk.W, padx=10, pady=5
        )
        self.ingredients_text = tk.Text(form_frame, width=40, height=3, font=self.manage_font.medium_letters_font)
        self.ingredients_text.grid(row=row, column=1, padx=10, pady=5)
        row += 1

        tk.Button(
            content, text="Get Recommendation",
            font=self.manage_font.medium_bold_letters_font,
            background="#333333", foreground="#FFFFFF",
            command=self.get_meal_recommendation
        ).pack(pady=10)

        self.result_frame = tk.Frame(content, background="#FFFFFF", relief=tk.GROOVE, bd=1)
        self.result_frame.pack(fill=tk.X, pady=10)

        self.result_label = tk.Label(
            self.result_frame, text="Recommendation will appear here.",
            font=self.manage_font.medium_letters_font, background="#FFFFFF",
            wraplength=800
        )
        self.result_label.pack(padx=10, pady=10)

        self.meal_details_frame = tk.Frame(content)
        self.meal_details_frame.pack(fill=tk.X)

        self._load_saved_meals()

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def get_meal_recommendation(self):
        try:
            user_input = {
                "MealType": self.combo_vars["meal_type"].get(),
                "Calories": float(self.entry_vars["calories"].get() or 0),
                "Protein": float(self.entry_vars["protein"].get() or 0),
                "Fat": float(self.entry_vars["fat"].get() or 0),
                "Carbohydrates": float(self.entry_vars["carbohydrates"].get() or 0),
                "Ingredients": self.ingredients_text.get("1.0", tk.END).strip(),
                "CookingTime": int(self.entry_vars["cooking_time"].get() or 0),
                "NutritionalGoals": self.combo_vars["nutritional_goals"].get(),
                "Budget": float(self.entry_vars["budget"].get() or 0),
                "DietaryRestrictions": self.combo_vars["dietary_restrictions"].get(),
                "Allergies": self.combo_vars["allergies"].get(),
                "MealSize": int(self.combo_vars["meal_size"].get() or 1),
            }
            recommendation = self.recommendation_engine.get_recommendation(user_input)
            self.result_label.config(text=recommendation)
            self._display_meal_details(recommendation.replace("Recommended Meal: ", ""))
        except Exception as e:
            self.message_handler.invalid_message(f"Error: \n\n \u26A0 Could not get recommendation: {e}")

    def _display_meal_details(self, meal_name):
        for widget in self.meal_details_frame.winfo_children():
            widget.destroy()

        try:
            conn = sqlite3.connect("FitZone.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT MealName, MealType, Calories, Protein, Fat, Carbohydrates, CookingTime, MealSummary FROM Meals WHERE MealName = ?",
                (meal_name,)
            )
            meal = cursor.fetchone()
            conn.close()

            if meal:
                details_frame = tk.Frame(self.meal_details_frame, background="#F0F0F0", relief=tk.GROOVE, bd=1)
                details_frame.pack(fill=tk.X, padx=10, pady=10)

                tk.Label(details_frame, text=f"Meal: {meal[0]}", font=self.manage_font.medium_bold_letters_font, background="#F0F0F0").pack(anchor=tk.W, padx=10)
                tk.Label(details_frame, text=f"Type: {meal[1]} | Calories: {meal[2]} kcal | Protein: {meal[3]}g | Fat: {meal[4]}g | Carbs: {meal[5]}g",
                         font=self.manage_font.smaller_letters_font, background="#F0F0F0").pack(anchor=tk.W, padx=10)
                tk.Label(details_frame, text=f"Cooking Time: {meal[6]} mins", font=self.manage_font.smaller_letters_font, background="#F0F0F0").pack(anchor=tk.W, padx=10)
                if meal[7]:
                    tk.Label(details_frame, text=f"Summary: {meal[7]}", font=self.manage_font.smaller_letters_font,
                             background="#F0F0F0", wraplength=800).pack(anchor=tk.W, padx=10, pady=(0, 10))
        except Exception as e:
            pass

    def _load_saved_meals(self):
        try:
            conn = sqlite3.connect("FitZone.db")
            cursor = conn.cursor()
            cursor.execute(
                """SELECT m.MealName, m.MealType, mp.PlanDate, mp.MealTime
                   FROM MealPlans mp JOIN Meals m ON mp.MealID = m.MealID
                   WHERE mp.MemberID = ? ORDER BY mp.PlanDate DESC LIMIT 10""",
                (self.member_id,)
            )
            saved = cursor.fetchall()
            conn.close()

            if saved:
                tk.Label(self.meal_details_frame, text="Your Saved Meal Plans:", font=self.manage_font.medium_bold_letters_font).pack(anchor=tk.W, padx=10, pady=(10, 0))
                for name, mtype, date, mtime in saved:
                    tk.Label(self.meal_details_frame, text=f"• {date} {mtime}: {name} ({mtype})",
                             font=self.manage_font.smaller_letters_font).pack(anchor=tk.W, padx=20)
        except Exception:
            pass
