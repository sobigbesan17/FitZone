import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
from gym_font import ManageFont
from gym_function_bank import MessageHandler
import datetime


class GymWorkoutsPage(GymBasePage):
    def __init__(self, member_id, location_id, home_callback, dashboard_callback=None):
        super().__init__()
        self.title("FitZone - Workouts")
        self.geometry("1100x700")
        self.member_id = member_id
        self.location_id = location_id
        self.home_callback = home_callback
        self.dashboard_callback = dashboard_callback

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)

        self.conn = sqlite3.connect("FitZone.db")
        self.cursor = self.conn.cursor()

        self.configure(background="#f2f2f2")
        self.create_workouts_page()

    def create_workouts_page(self):
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
        content.pack(fill=tk.X, pady=20, padx=40)

        nav_frame = tk.Frame(content, background="#333333")
        nav_frame.pack(fill=tk.X)
        tk.Button(
            nav_frame, text="\u2190 Back to Home",
            font=self.manage_font.medium_letters_font,
            background="#333333", foreground="#FFFFFF", relief=tk.FLAT,
            command=self.home_callback
        ).pack(side=tk.LEFT, padx=10, pady=5)

        if self.dashboard_callback:
            tk.Button(
                nav_frame, text="My Dashboard",
                font=self.manage_font.medium_letters_font,
                background="#FFE4B5", foreground="#000000",
                command=self.dashboard_callback
            ).pack(side=tk.RIGHT, padx=10, pady=5)

        tk.Label(content, text="Workout Library", font=self.manage_font.large_bold_heading_font).pack(anchor=tk.W, pady=(20, 5))
        tk.Label(content, text="Browse our comprehensive workout library to find the perfect exercise plan.",
                 font=self.manage_font.medium_letters_font).pack(anchor=tk.W, pady=(0, 10))

        filter_frame = tk.Frame(content)
        filter_frame.pack(fill=tk.X, pady=10)

        tk.Label(filter_frame, text="Type:", font=self.manage_font.medium_bold_letters_font).grid(row=0, column=0, padx=5)
        self.workout_type_var = tk.StringVar(value="All")
        workout_types = ["All", "Cardio", "Strength", "Flexibility", "HIIT", "Swimming", "Yoga", "Pilates"]
        ttk.Combobox(
            filter_frame,
            textvariable=self.workout_type_var,
            values=workout_types,
            state="readonly",
            width=15,
            font=self.manage_font.medium_letters_font,
        ).grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Difficulty:", font=self.manage_font.medium_bold_letters_font).grid(row=0, column=2, padx=5)
        self.difficulty_var = tk.StringVar(value="All")
        difficulties = ["All", "Beginner", "Intermediate", "Advanced"]
        ttk.Combobox(
            filter_frame,
            textvariable=self.difficulty_var,
            values=difficulties,
            state="readonly",
            width=15,
            font=self.manage_font.medium_letters_font,
        ).grid(row=0, column=3, padx=5)

        tk.Label(filter_frame, text="Goal:", font=self.manage_font.medium_bold_letters_font).grid(row=0, column=4, padx=5)
        self.goal_var = tk.StringVar(value="All")
        goals = ["All", "Weight Loss", "Muscle Gain", "Endurance", "Flexibility", "General Fitness"]
        ttk.Combobox(
            filter_frame,
            textvariable=self.goal_var,
            values=goals,
            state="readonly",
            width=18,
            font=self.manage_font.medium_letters_font,
        ).grid(row=0, column=5, padx=5)

        self.workouts_content_frame = tk.Frame(content)
        self.workouts_content_frame.pack(fill=tk.X)

        tk.Button(
            filter_frame, text="Apply Filter",
            font=self.manage_font.medium_letters_font,
            background="#333333", foreground="#FFFFFF",
            command=self.load_workouts
        ).grid(row=0, column=6, padx=10)

        self.load_workouts()
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def load_workouts(self):
        for widget in self.workouts_content_frame.winfo_children():
            widget.destroy()

        try:
            query = "SELECT WorkoutID, WorkoutName, WorkoutType, WorkoutGoal, Difficulty, Equipment, WarmupDuration, CooldownDuration, Description FROM Workouts WHERE 1=1"
            params = []

            if self.workout_type_var.get() != "All":
                query += " AND WorkoutType = ?"
                params.append(self.workout_type_var.get())

            if self.difficulty_var.get() != "All":
                query += " AND Difficulty = ?"
                params.append(self.difficulty_var.get())

            if self.goal_var.get() != "All":
                query += " AND WorkoutGoal = ?"
                params.append(self.goal_var.get())

            query += " ORDER BY WorkoutName ASC"

            self.cursor.execute(query, params)
            workouts = self.cursor.fetchall()

            if not workouts:
                tk.Label(
                    self.workouts_content_frame,
                    text="No workouts found matching your criteria.",
                    font=self.manage_font.medium_letters_font
                ).pack(pady=20)
                return

            for i, workout in enumerate(workouts):
                wid, name, wtype, goal, difficulty, equipment, warmup, cooldown, desc = workout

                card = tk.Frame(self.workouts_content_frame, background="#FFFFFF", relief=tk.GROOVE, bd=1)
                card.pack(fill=tk.X, pady=8)

                header_bg = "#F0F8FF" if i % 2 == 0 else "#FFF5E6"
                header = tk.Frame(card, background=header_bg)
                header.pack(fill=tk.X, padx=10, pady=5)

                tk.Label(header, text=name, font=self.manage_font.larger_bold_letters_font, background=header_bg).pack(side=tk.LEFT)

                diff_colors = {"Beginner": "#4CAF50", "Intermediate": "#FF9800", "Advanced": "#D11A17"}
                tk.Label(
                    header, text=difficulty or "Unknown",
                    font=self.manage_font.smaller_letters_font,
                    background=diff_colors.get(difficulty, "#333333"),
                    foreground="#FFFFFF", padx=5
                ).pack(side=tk.RIGHT, padx=5)

                info_frame = tk.Frame(card, background="#FFFFFF")
                info_frame.pack(fill=tk.X, padx=10, pady=5)

                stats = f"Type: {wtype} | Goal: {goal} | Equipment: {equipment} | Warmup: {warmup} min | Cooldown: {cooldown} min"
                tk.Label(info_frame, text=stats, font=self.manage_font.smaller_letters_font, background="#FFFFFF").pack(anchor=tk.W)

                if desc:
                    tk.Label(info_frame, text=desc, font=self.manage_font.smaller_letters_font,
                             background="#FFFFFF", foreground="#555555", wraplength=900).pack(anchor=tk.W, pady=3)

                self._load_exercises(info_frame, wid)

                if self.member_id:
                    tk.Button(
                        card, text="Add to Workout Plan",
                        font=self.manage_font.smaller_letters_font,
                        background="#333333", foreground="#FFFFFF",
                        command=lambda wid_=wid, wn=name: self.add_to_workout_plan(wid_, wn)
                    ).pack(anchor=tk.E, padx=10, pady=5)

        except sqlite3.Error as e:
            self.message_handler.invalid_message(f"Error loading workouts: {e}")

    def _load_exercises(self, parent, workout_id):
        try:
            self.cursor.execute(
                "SELECT ExerciseName, Sets, Reps, DurationSeconds FROM Exercises WHERE WorkoutID = ?",
                (workout_id,)
            )
            exercises = self.cursor.fetchall()

            if exercises:
                tk.Label(parent, text="Exercises:", font=self.manage_font.medium_bold_letters_font, background="#FFFFFF").pack(anchor=tk.W, pady=(5, 0))
                for ex in exercises:
                    name, sets, reps, duration = ex
                    ex_text = f"• {name}: {sets} sets x {reps} reps"
                    if duration:
                        ex_text += f" ({duration}s)"
                    tk.Label(parent, text=ex_text, font=self.manage_font.smaller_letters_font,
                             background="#FFFFFF", foreground="#333333").pack(anchor=tk.W, padx=15)
        except Exception:
            pass

    def add_to_workout_plan(self, workout_id, workout_name):
        try:
            plan_date = datetime.date.today()
            self.cursor.execute(
                "INSERT INTO WorkoutPlans (MemberID, WorkoutID, PlanDate) VALUES (?, ?, ?)",
                (self.member_id, workout_id, plan_date)
            )
            self.conn.commit()
            self.message_handler.success_message(f"Success: \n\n \u2705 '{workout_name}' added to your workout plan!")
        except sqlite3.Error as e:
            self.message_handler.invalid_message(f"Error: \n\n \u26A0 Could not add to workout plan: {e}")
