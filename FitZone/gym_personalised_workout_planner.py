import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
from gym_font import ManageFont
from gym_function_bank import MessageHandler
from gym_workout_recommendation_algorithm import GymWorkoutRecommendationAlgorithm


class PersonalisedWorkoutPlannerPage(GymBasePage):
    def __init__(self, member_id, fitness_dashboard_callback, calculate_bmi_callback,
                 bmi_visualisation_callback, gym_meal_planner_callback,
                 gym_workout_planner_callback, view_class_schedule_callback,
                 gym_class_booking_callback, gym_class_clashes_callback):
        super().__init__()
        self.title("FitZone - Personalised Workout Planner")
        self.geometry("1000x700")
        self.member_id = member_id

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)

        self.recommendation_engine = GymWorkoutRecommendationAlgorithm()
        self.recommendation_engine.load_data()
        self.recommendation_engine.preprocess_data()

        self.configure(background="#f2f2f2")
        self.create_workout_planner_page()

    def create_workout_planner_page(self):
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

        tk.Label(content, text="Personalised Workout Planner", font=self.manage_font.large_bold_heading_font).pack(anchor=tk.W)
        tk.Label(content, text="Enter your preferences to get personalised workout recommendations.",
                 font=self.manage_font.medium_letters_font).pack(anchor=tk.W, pady=(0, 20))

        form_frame = tk.Frame(content)
        form_frame.pack(fill=tk.X)

        combo_fields = [
            ("Workout Type:", "workout_type", ["Cardio", "Strength", "Flexibility", "HIIT", "Swimming", "Yoga", "Pilates"]),
            ("Workout Goal:", "workout_goal", ["Weight Loss", "Muscle Gain", "Endurance", "Flexibility", "General Fitness"]),
            ("Difficulty Level:", "difficulty", ["Beginner", "Intermediate", "Advanced"]),
            ("Equipment:", "equipment", ["None", "Dumbbells", "Barbell", "Resistance Bands", "Kettlebell", "Swimsuit", "Yoga Mat"]),
        ]

        self.combo_vars = {}
        row = 0
        for label_text, key, values in combo_fields:
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
            ("Warmup Duration (min):", "warmup_duration"),
            ("Cooldown Duration (min):", "cooldown_duration"),
        ]

        self.entry_vars = {}
        for label_text, key in numeric_fields:
            tk.Label(form_frame, text=label_text, font=self.manage_font.medium_bold_letters_font).grid(
                row=row, column=0, sticky=tk.W, padx=10, pady=5
            )
            var = tk.StringVar(value="5")
            self.entry_vars[key] = var
            entry = ttk.Entry(form_frame, textvariable=var, width=42, font=self.manage_font.medium_letters_font)
            entry.grid(row=row, column=1, padx=10, pady=5)
            row += 1

        tk.Button(
            content, text="Get Recommendation",
            font=self.manage_font.medium_bold_letters_font,
            background="#333333", foreground="#FFFFFF",
            command=self.get_workout_recommendation
        ).pack(pady=10)

        self.result_frame = tk.Frame(content, background="#FFFFFF", relief=tk.GROOVE, bd=1)
        self.result_frame.pack(fill=tk.X, pady=10)

        self.result_label = tk.Label(
            self.result_frame, text="Recommendation will appear here.",
            font=self.manage_font.medium_letters_font, background="#FFFFFF"
        )
        self.result_label.pack(padx=10, pady=10)

        self.workout_details_frame = tk.Frame(content)
        self.workout_details_frame.pack(fill=tk.X)

        self._load_saved_workouts()

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def get_workout_recommendation(self):
        try:
            user_input = {
                "WorkoutType": self.combo_vars["workout_type"].get(),
                "WorkoutGoal": self.combo_vars["workout_goal"].get(),
                "Difficulty": self.combo_vars["difficulty"].get(),
                "Equipment": self.combo_vars["equipment"].get(),
                "WarmupDuration": int(self.entry_vars["warmup_duration"].get() or 5),
                "CooldownDuration": int(self.entry_vars["cooldown_duration"].get() or 5),
            }
            recommendation = self.recommendation_engine.get_recommendation(user_input)
            self.result_label.config(text=recommendation)
            self._display_workout_details(recommendation.replace("Recommended Workout: ", ""))
        except Exception as e:
            self.message_handler.invalid_message(f"Error: \n\n \u26A0 Could not get recommendation: {e}")

    def _display_workout_details(self, workout_name):
        for widget in self.workout_details_frame.winfo_children():
            widget.destroy()

        try:
            conn = sqlite3.connect("FitZone.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT WorkoutName, WorkoutType, WorkoutGoal, Difficulty, Equipment, WarmupDuration, CooldownDuration, Description FROM Workouts WHERE WorkoutName = ?",
                (workout_name,)
            )
            workout = cursor.fetchone()

            if workout:
                cursor.execute(
                    "SELECT ExerciseName, Sets, Reps, DurationSeconds, Description FROM Exercises WHERE WorkoutID = (SELECT WorkoutID FROM Workouts WHERE WorkoutName = ?)",
                    (workout_name,)
                )
                exercises = cursor.fetchall()
            conn.close()

            if workout:
                details_frame = tk.Frame(self.workout_details_frame, background="#F0F0F0", relief=tk.GROOVE, bd=1)
                details_frame.pack(fill=tk.X, padx=10, pady=10)

                tk.Label(details_frame, text=f"Workout: {workout[0]}", font=self.manage_font.medium_bold_letters_font, background="#F0F0F0").pack(anchor=tk.W, padx=10)
                tk.Label(details_frame, text=f"Type: {workout[1]} | Goal: {workout[2]} | Difficulty: {workout[3]}",
                         font=self.manage_font.smaller_letters_font, background="#F0F0F0").pack(anchor=tk.W, padx=10)
                tk.Label(details_frame, text=f"Equipment: {workout[4]} | Warmup: {workout[5]} min | Cooldown: {workout[6]} min",
                         font=self.manage_font.smaller_letters_font, background="#F0F0F0").pack(anchor=tk.W, padx=10)

                if exercises:
                    tk.Label(details_frame, text="Exercises:", font=self.manage_font.medium_bold_letters_font, background="#F0F0F0").pack(anchor=tk.W, padx=10, pady=(5, 0))
                    for ex in exercises:
                        tk.Label(details_frame, text=f"• {ex[0]}: {ex[1]} sets x {ex[2]} reps ({ex[3]}s)",
                                 font=self.manage_font.smaller_letters_font, background="#F0F0F0").pack(anchor=tk.W, padx=20)
        except Exception:
            pass

    def _load_saved_workouts(self):
        try:
            conn = sqlite3.connect("FitZone.db")
            cursor = conn.cursor()
            cursor.execute(
                """SELECT w.WorkoutName, w.WorkoutType, wp.PlanDate
                   FROM WorkoutPlans wp JOIN Workouts w ON wp.WorkoutID = w.WorkoutID
                   WHERE wp.MemberID = ? ORDER BY wp.PlanDate DESC LIMIT 10""",
                (self.member_id,)
            )
            saved = cursor.fetchall()
            conn.close()

            if saved:
                tk.Label(self.workout_details_frame, text="Your Saved Workout Plans:", font=self.manage_font.medium_bold_letters_font).pack(anchor=tk.W, padx=10, pady=(10, 0))
                for name, wtype, date in saved:
                    tk.Label(self.workout_details_frame, text=f"• {date}: {name} ({wtype})",
                             font=self.manage_font.smaller_letters_font).pack(anchor=tk.W, padx=20)
        except Exception:
            pass
