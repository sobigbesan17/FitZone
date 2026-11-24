import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
import sqlite3
from gym_function_bank import MessageHandler, ManageFont
from PIL import Image, ImageTk
import math
import datetime
import matplotlib
import matplotlib.figure
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches
import numpy as np


class FitnessDashboardPage(GymBasePage):
    def __init__(self, member_id, fitness_dashboard_callback, calculate_bmi_callback,
                 bmi_visualisation_callback, gym_meal_planner_callback,
                 gym_workout_planner_callback, view_class_schedule_callback,
                 gym_class_booking_callback, gym_class_clashes_callback):
        super().__init__()
        self.title("Fitness Dashboard")
        self.geometry("1200x800")
        self.member_id = member_id
        self.steps = None
        self.distance = None
        self.calories_burned = None
        self.workouts = None
        self.target_steps = None
        self.target_distance = None
        self.target_calories_burned = None
        self.target_workouts = None
        self.workouts_last_seven_days = None
        self.dashboard_frame = True
        self.filter_title_frame = None

        self.conn = sqlite3.connect("FitZone.db")
        self.cursor = self.conn.cursor()

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)

        self.start_date = datetime.date.today()
        self.header_date = self.start_date

        self._ensure_fitness_table()
        self.load_fitness_data()
        self.load_member_name()

        self.create_dashboard()

    def _ensure_fitness_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS FitnessDashboard (
                    DashboardID INTEGER PRIMARY KEY AUTOINCREMENT,
                    MemberID INTEGER,
                    Date DATE,
                    Steps INTEGER DEFAULT 0,
                    Distance DECIMAL(5,2) DEFAULT 0,
                    CaloriesBurned INTEGER DEFAULT 0,
                    Workouts INTEGER DEFAULT 0,
                    TargetSteps INTEGER DEFAULT 10000,
                    TargetDistance DECIMAL(5,2) DEFAULT 5.0,
                    TargetCaloriesBurned INTEGER DEFAULT 500,
                    TargetWorkouts INTEGER DEFAULT 3,
                    BreakfastCalories INTEGER DEFAULT 0,
                    LunchCalories INTEGER DEFAULT 0,
                    DinnerCalories INTEGER DEFAULT 0,
                    FOREIGN KEY (MemberID) REFERENCES Members(MemberID)
                )
            """)
            self.conn.commit()
        except Exception:
            pass

    def refresh_dashboard(self):
        if self.filter_title_frame:
            try:
                self.filter_title_frame.destroy()
            except Exception:
                pass
        if self.dashboard_frame and isinstance(self.dashboard_frame, tk.Widget):
            try:
                self.dashboard_frame.destroy()
            except Exception:
                pass
        try:
            self.canvas.destroy()
        except Exception:
            pass
        try:
            self.page.destroy()
        except Exception:
            pass
        self.dashboard_frame = True
        self.load_fitness_data()
        self.create_dashboard()

    def load_fitness_data(self):
        query = """
            SELECT Steps, Distance, CaloriesBurned, Workouts,
                   TargetSteps, TargetDistance, TargetCaloriesBurned, TargetWorkouts,
                   BreakfastCalories, LunchCalories, DinnerCalories
            FROM FitnessDashboard
            WHERE MemberID = ? AND Date = ?
        """
        self.cursor.execute(query, (self.member_id, self.start_date))
        self.fitness_data = self.cursor.fetchone()

        if self.fitness_data:
            (self.steps, self.distance, self.calories_burned, self.workouts,
             self.target_steps, self.target_distance, self.target_calories_burned,
             self.target_workouts, self.breakfast_calories, self.lunch_calories,
             self.dinner_calories) = self.fitness_data
            self.last_seven_days, self.workouts_last_seven_days, self.target_workouts_last_seven_days = (
                self.load_workouts_last_seven_days()
            )
        else:
            self.steps = self.distance = self.calories_burned = self.workouts = None
            self.target_steps = 10000
            self.target_distance = 5.0
            self.target_calories_burned = 500
            self.target_workouts = 3
            self.breakfast_calories = self.lunch_calories = self.dinner_calories = 0
            self.last_seven_days = []
            self.workouts_last_seven_days = []
            self.target_workouts_last_seven_days = []

    def load_member_name(self):
        query = "SELECT FirstName, LastName FROM Members WHERE MemberID = ?"
        self.cursor.execute(query, (self.member_id,))
        result = self.cursor.fetchone()
        if result:
            self.first_name, self.last_name = result
        else:
            self.first_name = "Member"
            self.last_name = ""

    def load_workouts_last_seven_days(self):
        query = """
            SELECT Date, Workouts, TargetWorkouts
            FROM FitnessDashboard
            WHERE MemberID = ? AND Date >= ? AND Date <= ?
        """
        upper_date = self.start_date
        lower_date = upper_date - datetime.timedelta(days=6)
        self.cursor.execute(query, (self.member_id, lower_date, upper_date))
        workouts_data = self.cursor.fetchall()

        dates_last_seven_days = [data[0] for data in workouts_data]
        number_of_workouts_last_seven_days = [data[1] for data in workouts_data]
        number_of_target_workouts_last_seven_days = [data[2] for data in workouts_data]
        return dates_last_seven_days, number_of_workouts_last_seven_days, number_of_target_workouts_last_seven_days

    def create_dashboard(self):
        self.page = tk.Frame(self)
        self.page.pack(side="top", fill="both", expand=True)

        self.filter_title_frame = ttk.Label(
            self.page, text="Fitness Dashboard:",
            font=self.manage_font.large_bold_heading_font,
            background="#333333", foreground="#FFFFFF"
        )
        self.filter_title_frame.pack(side="top", fill="x")

        self.refresh_button = tk.Button(
            self.filter_title_frame,
            text="↻",
            command=self.refresh_dashboard,
            font=("Segoe UI Symbol", 18, "bold"),
            background="#333333",
            foreground="#FFFFFF",
            activebackground="#444444",
            activeforeground="#FFFFFF",
            bd=0,
            relief=tk.FLAT,
            width=4,
            height=1,
            cursor="hand2",
        )
        self.refresh_button.pack(side="right", padx=30, pady=5)

        self.body_frame = tk.Frame(self.page)
        self.body_frame.pack(side="top", fill="both", expand=True)

        if self.dashboard_frame:
            self.dashboard_frame = ttk.Frame(self.body_frame)
            self.dashboard_frame.pack(side="top", fill="x", pady=20)

            date_frame = tk.Frame(self.dashboard_frame, background="#444444")
            date_frame.pack(fill="x", anchor="center")

            header_date = self.header_date

            left_arrow = tk.Button(
                date_frame, text="\u2190",
                font=self.manage_font.medium_bold_heading_font,
                command=self.go_to_prev_week, background="#FFE4B5"
            )
            left_arrow.grid(row=0, column=0, rowspan=2, padx=(10, 5), pady=0, sticky="w")

            right_arrow = tk.Button(
                date_frame, text="\u2192",
                font=self.manage_font.medium_bold_heading_font,
                command=self.go_to_next_week, background="#FFE4B5"
            )
            right_arrow.grid(row=0, column=8, rowspan=2, padx=(10, 5), pady=0, sticky="e")

            self.categories = []
            for i in range(7):
                formatted_date = header_date.strftime("%Y-%m-%d")
                day_of_week = header_date.strftime("%A")
                tk.Button(
                    date_frame, text=formatted_date,
                    font=self.manage_font.medium_bold_heading_font,
                    background="#444444", foreground="white",
                    command=lambda date=formatted_date: self.go_to_date(date)
                ).grid(row=0, column=i + 1, padx=50, pady=0)
                tk.Label(
                    date_frame, text=day_of_week,
                    font=self.manage_font.smaller_letters_font,
                    background="#444444", foreground="white"
                ).grid(row=1, column=i + 1, padx=50, pady=0, sticky="ew")
                self.categories.append(formatted_date)
                header_date += datetime.timedelta(days=1)

            welcome_frame = tk.Frame(self.dashboard_frame, background="#444444")
            welcome_frame.pack(fill="x")
            tk.Label(
                welcome_frame,
                text=f"Welcome, {self.first_name} {self.last_name}!",
                font=self.manage_font.large_bold_letters_font,
                background="#444444", foreground="white"
            ).pack(side="left", padx=10)

            self.activity_frame = tk.Frame(self.dashboard_frame, background="#444444")
            self.activity_frame.pack(fill="x")
            tk.Label(
                self.activity_frame, text="Daily Task:",
                font=self.manage_font.medium_bold_heading_font,
                background="#444444", foreground="white"
            ).pack(padx=10)

            self.create_all_tasks()

        self.canvas = tk.Canvas(self.body_frame, background="white")
        self.canvas.pack(side="top", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.canvas, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.content_frame = tk.Frame(self.canvas, background="#FFFFFF")
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        self.add_content()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", self.configure_canvas)

    def close_filter(self):
        if self.dashboard_frame and isinstance(self.dashboard_frame, tk.Widget):
            try:
                self.dashboard_frame.destroy()
            except Exception:
                pass
        self.dashboard_frame = None
        self.refresh_dashboard()
        try:
            self.dropdown_label.configure(text="\u25B2")
        except Exception:
            pass

    def open_filter(self):
        if self.dashboard_frame and isinstance(self.dashboard_frame, tk.Widget):
            self.close_filter()
        else:
            self.dashboard_frame = True
            try:
                self.canvas.destroy()
            except Exception:
                pass
            self.refresh_dashboard()
            try:
                self.dropdown_label.configure(text="\u25BC")
            except Exception:
                pass

    def create_all_tasks(self):
        self.main_colour = "#1CBAFF"
        self.secondary_colour = "#1AABEA"
        self.create_task_frame("Do 50 Pushups then do a jog around the garden", "7:00PM")

    def create_task_frame(self, task, time):
        task_frame = tk.Frame(self.activity_frame, background="#444444")
        task_frame.pack(fill="x", padx=10, pady=10)
        task_frame.grid_columnconfigure(0, weight=1)
        task_frame.grid_columnconfigure(1, weight=0)

        text_widget = tk.Text(
            task_frame, font=self.manage_font.medium_bold_letters_font,
            background=self.main_colour, foreground="#FFFFFF",
            height=5, width=100, borderwidth=0
        )
        text_widget.grid(row=0, column=0, sticky="nsew")
        text_widget.insert("1.0", task)
        text_widget.config(state="disabled")

        time_widget = tk.Text(
            task_frame, font=self.manage_font.large_bold_heading_font,
            background=self.secondary_colour, foreground="#FFFFFF",
            height=5, width=10, borderwidth=0
        )
        time_widget.grid(row=0, column=1, sticky="ns", padx=(10, 0))
        time_widget.insert("1.0", time)
        time_widget.config(state="disabled")

    def go_to_prev_week(self):
        self.header_date -= datetime.timedelta(days=7)
        self.refresh_dashboard()

    def go_to_date(self, date):
        formatted_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        self.start_date = formatted_date
        self.refresh_dashboard()

    def go_to_next_week(self):
        self.header_date += datetime.timedelta(days=7)
        self.refresh_dashboard()

    def configure_canvas(self, event):
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def add_content(self):
        tk.Label(
            self.content_frame, text="Fitness Dashboard",
            font=self.manage_font.heading_font, background="#FFFFFF"
        ).pack(padx=(250, 5), pady=0)
        tk.Label(
            self.content_frame, text=str(self.start_date),
            font=self.manage_font.medium_bold_letters_font, background="#FFFFFF"
        ).pack(padx=(250, 5), pady=0)

        ttk.Separator(self.content_frame, orient="horizontal").pack(fill="x")

        if self.fitness_data:
            self.top_pie_chart_frame = tk.Frame(self.content_frame, background="#FFFFFF")
            self.top_pie_chart_frame.pack(fill="x")

            self.create_steps_left_pie_chart()
            self.create_distance_pie_chart()
            self.create_calories_burned_pie_chart()
            self.create_workouts_over_last_seven_days()
            self.create_workouts_left_pie_chart()
            self.create_goals_left_pie_chart()
            self.create_weight_progress_graph()
            self.create_meal_statistics_graph()
        else:
            tk.Label(
                self.content_frame,
                text="No fitness data for the selected date.",
                font=self.manage_font.medium_bold_letters_font, background="#FFFFFF"
            ).pack(padx=(250, 5), pady=20)

    def create_steps_left_pie_chart(self):
        self.background = "#ADD8E6"
        self.figsize = (2, 2)
        workouts_frame = tk.Frame(self.top_pie_chart_frame, background=self.background, padx=20, pady=20)
        workouts_frame.grid(padx=20, pady=20, row=0, column=0)
        tk.Label(workouts_frame, text="Steps taken this week", font=self.manage_font.medium_letters_font, background=self.background).pack()
        self.categories = [f"Done: {self.steps} steps", f"Goal:{self.target_steps} steps"]
        self.steps_percentage = int((self.steps / self.target_steps) * 100) if self.target_steps else 0
        self.pie_chart_data = [self.steps_percentage, 100 - self.steps_percentage]
        self.pie_chart_colors = ["#1CBAFF", "#ECF0F1"]
        self.create_pie_chart(workouts_frame, False)
        self.pie_chart_canvas.get_tk_widget().pack(padx=(10, 5), pady=0, side="left")

    def create_distance_pie_chart(self):
        self.background = "#FFCCCC"
        distance_travelled_frame = tk.Frame(self.top_pie_chart_frame, background=self.background, padx=20, pady=20)
        distance_travelled_frame.grid(padx=20, pady=20, row=0, column=1)
        tk.Label(distance_travelled_frame, text="Distance Travelled", font=self.manage_font.medium_letters_font, background=self.background).pack()
        self.categories = [f"Done: {self.distance}kms", f"Goal:{self.target_distance}kms"]
        self.distance_percentage = int((self.distance / self.target_distance) * 100) if self.target_distance else 0
        self.pie_chart_data = [self.distance_percentage, 100 - self.distance_percentage]
        self.pie_chart_colors = ["#F6433F", "#ECF0F1"]
        self.create_pie_chart(distance_travelled_frame, False)
        self.pie_chart_canvas.get_tk_widget().pack(padx=(10, 5), pady=0, side="left")

    def create_calories_burned_pie_chart(self):
        self.background = "#FFFF99"
        calories_burned_frame = tk.Frame(self.top_pie_chart_frame, background=self.background, padx=20, pady=20)
        calories_burned_frame.grid(padx=20, pady=20, row=0, column=2)
        tk.Label(calories_burned_frame, text="Calories Burned", font=self.manage_font.medium_letters_font, background=self.background).pack()
        self.categories = [f"Done: {self.calories_burned}cals", f"Goal:{self.target_calories_burned}cals"]
        self.calories_burned_percentage = int((self.calories_burned / self.target_calories_burned) * 100) if self.target_calories_burned else 0
        self.pie_chart_data = [self.calories_burned_percentage, 100 - self.calories_burned_percentage]
        self.pie_chart_colors = ["#FFC602", "#ECF0F1"]
        self.create_pie_chart(calories_burned_frame, False)
        self.pie_chart_canvas.get_tk_widget().pack(padx=(10, 5), pady=0, side="left")

    def create_workouts_left_pie_chart(self):
        self.background = "#98FB98"
        self.figsize = (2, 2)
        workouts_frame = tk.Frame(self.top_pie_chart_frame, background=self.background, padx=20, pady=20)
        workouts_frame.grid(padx=20, pady=20, row=0, column=3)
        tk.Label(workouts_frame, text="Workouts", font=self.manage_font.medium_letters_font, background=self.background).pack()
        self.categories = [f"Done: {self.workouts} workouts", f"Goal:{self.target_workouts} workouts"]
        self.workout_percentage = int((self.workouts / self.target_workouts) * 100) if self.target_workouts else 0
        self.pie_chart_data = [self.workout_percentage, 100 - self.workout_percentage]
        self.pie_chart_colors = ["#228B22", "#ECF0F1"]
        self.create_pie_chart(workouts_frame, False)
        self.pie_chart_canvas.get_tk_widget().pack(padx=(10, 5), pady=0, side="left")

    def create_workouts_over_last_seven_days(self):
        if not self.last_seven_days or not self.workouts_last_seven_days:
            return
        self.background = "#FFFFFF"
        self.figsize = (5, 5)
        self.categories = self.last_seven_days
        number_of_workout = self.workouts_last_seven_days
        self.bar_chart_colors1 = ["red", "green", "blue", "orange", "purple", "pink", "brown"]
        target_workout = [
            max(0, target - workout)
            for target, workout in zip(self.target_workouts_last_seven_days, self.workouts_last_seven_days)
        ]
        self.bar_chart_colors2 = ["#F9F9F9", "#F5F5F5", "#F0F0F0", "#EAEAEA", "#E5E5E5", "#E0E0E0", "#DADADA"]
        self.bar_chart_x_label = "Day"
        self.bar_chart_y_label = "Number of Workouts"
        self.bar_chart_title = "Number of Workouts over the last 7 days"
        workout_bar_chart_frame = tk.Frame(self.top_pie_chart_frame, background=self.background, padx=20, pady=0)
        workout_bar_chart_frame.grid(row=1, column=0, columnspan=2)
        self.create_stacked_bar_chart(workout_bar_chart_frame, number_of_workout, "Complete Workouts", target_workout, "Incomplete Workouts")
        self.bar_chart_canvas.get_tk_widget().pack(padx=(10, 5), pady=0, side="left")

    def create_goals_left_pie_chart(self):
        self.background = "#333333"
        self.figsize = (5, 5)
        goals_frame = tk.Frame(self.top_pie_chart_frame, background=self.background, padx=20, pady=20)
        goals_frame.grid(padx=20, pady=20, row=1, column=2, columnspan=2)

        steps_pct = getattr(self, "steps_percentage", 0)
        distance_pct = getattr(self, "distance_percentage", 0)
        calories_pct = getattr(self, "calories_burned_percentage", 0)
        workout_pct = getattr(self, "workout_percentage", 0)

        self.goal_percentage_data = [steps_pct / 8, distance_pct / 8, calories_pct / 8, workout_pct / 8]
        total_goal_achieved = int(2 * sum(self.goal_percentage_data))
        incomplete_goals_percentage = (100 - total_goal_achieved) / 2
        self.pie_chart_data = self.goal_percentage_data + [incomplete_goals_percentage, 50]
        tk.Label(
            goals_frame, text=f"Goal ({total_goal_achieved}%)",
            font=self.manage_font.larger_letters_font, background="#333333", foreground="#FFFFFF"
        ).pack(fill="x")
        self.categories = ["Steps", "Distance", "Calories Burned", "Workouts"]
        self.pie_chart_colors = ["#1CBAFF", "#F6433F", "#FFC602", "#228B22", "#222222", self.background]

        fig = matplotlib.figure.Figure(figsize=self.figsize)
        fig.patch.set_facecolor(self.background)
        ax = fig.add_subplot(111)
        ax.pie(self.pie_chart_data, startangle=180, counterclock=False, colors=self.pie_chart_colors)
        ax.legend(self.categories)
        circle = matplotlib.patches.Circle((0, 0), 0.7, color=self.background)
        ax.add_artist(circle)
        self.pie_chart_canvas = FigureCanvasTkAgg(fig, master=goals_frame)
        self.pie_chart_canvas.get_tk_widget().pack(padx=(10, 5), pady=0, side="right")

    def create_weight_progress_graph(self):
        if not self.last_seven_days or len(self.last_seven_days) < 2:
            return
        self.background = "#30257D"
        self.spline_graph_colour = "#FFFFFF"
        self.categories = self.last_seven_days
        self.spline_data = self.workouts_last_seven_days
        self.graph_x_label = "Day"
        self.graph_y_label = "Number of Workouts"
        self.graph_title = "Workouts Statistics over the last 7 days"
        workout_graph_frame = tk.Frame(self.top_pie_chart_frame, padx=20, pady=0, background="#FFFFFF")
        workout_graph_frame.grid(padx=20, pady=20, row=3, column=0, columnspan=4)
        self.create_spline_graph(workout_graph_frame)
        self.graph_canvas.get_tk_widget().pack(padx=(10, 5), pady=0, side="left")

    def create_meal_statistics_graph(self):
        self.background = "#30257D"
        self.spline_graph_colour = "#FFFFFF"
        self.categories = ["Breakfast", "Lunch", "Dinner"]
        self.spline_data = [
            self.breakfast_calories or 0,
            self.lunch_calories or 0,
            self.dinner_calories or 0
        ]
        self.graph_x_label = "Meal Type"
        self.graph_y_label = "Calories (kcal)"
        self.graph_title = "Meal Statistics"
        meal_graph_frame = tk.Frame(self.top_pie_chart_frame, padx=20, pady=0, background="#FFFFFF")
        meal_graph_frame.grid(padx=20, pady=20, row=4, column=0, columnspan=4)
        self.create_spline_graph(meal_graph_frame)
        self.graph_canvas.get_tk_widget().pack(padx=(10, 5), pady=0, side="left")

    def create_pie_chart(self, parent_frame, semicircle):
        fig = matplotlib.figure.Figure(figsize=self.figsize)
        fig.patch.set_facecolor(self.background)
        ax = fig.add_subplot(111)
        if semicircle:
            ax.pie(self.pie_chart_data, startangle=0, counterclock=False, colors=self.pie_chart_colors)
        else:
            ax.pie(self.pie_chart_data, startangle=90, counterclock=False, colors=self.pie_chart_colors)
        ax.legend(self.categories)
        circle = matplotlib.patches.Circle((0, 0), 0.7, color=self.background)
        ax.add_artist(circle)
        self.pie_chart_canvas = FigureCanvasTkAgg(fig, master=parent_frame)

    def create_stacked_bar_chart(self, parent_frame, bar_chart_data1, label_data1, bar_chart_data2, label_data2):
        fig = matplotlib.figure.Figure(figsize=(5, 5), dpi=100, facecolor="#333333")
        ax = fig.add_subplot(111, facecolor="#333333")
        ind = np.arange(len(self.categories))
        width = 0.5
        rects1 = ax.bar(ind, bar_chart_data1, width, color=self.bar_chart_colors1[:len(ind)])
        rects2 = ax.bar(ind, bar_chart_data2, width, color=self.bar_chart_colors2[:len(ind)], bottom=bar_chart_data1)
        for spine in ax.spines.values():
            spine.set_color("white")
        ax.tick_params(axis="x", colors="white")
        ax.tick_params(axis="y", colors="white")
        ax.set_xlabel(self.bar_chart_x_label, color="white")
        ax.set_ylabel(self.bar_chart_y_label, color="white")
        ax.set_title(self.bar_chart_title, color="white")
        ax.legend((rects1[0], rects2[0]), (label_data1, label_data2))
        max_val = max(bar_chart_data1) + max(bar_chart_data2) if bar_chart_data1 and bar_chart_data2 else 1
        ax.set_yticks(np.arange(0, max_val + 1, 1))
        ax.set_xticks(ind)
        ax.set_xticklabels(self.categories, rotation=45, ha="right", fontsize=10, color="white")
        self.bar_chart_canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        self.bar_chart_canvas.draw()

    def create_spline_graph(self, parent_frame):
        fig = matplotlib.figure.Figure(figsize=(12, 4), dpi=100)
        ax = fig.add_subplot(111)
        fig.patch.set_facecolor(self.background)
        x = np.arange(len(self.categories))
        y = np.array(self.spline_data, dtype=float)

        if len(x) >= 2:
            k = min(len(self.spline_data) - 1, 3)
            x_new = np.linspace(x.min(), x.max(), 300)
            spl = make_interp_spline(x, y, k=k)
            y_new = spl(x_new)
            ax.plot(x_new, y_new, label="Spline Curve", color=self.spline_graph_colour)
        ax.scatter(x, y, marker="o", color=self.spline_graph_colour, label="Data Points")

        for spine in ax.spines.values():
            spine.set_color("white")
        ax.tick_params(axis="x", colors="white")
        ax.tick_params(axis="y", colors="white")
        ax.set_facecolor(color=self.background)
        ax.set_xlabel(self.graph_x_label, color="#FFFFFF")
        ax.set_ylabel(self.graph_y_label, color="#FFFFFF")
        ax.set_title(self.graph_title, color="#FFFFFF")
        ax.set_xticks(x)
        ax.set_xticklabels(self.categories, fontsize=10, color="white")
        ax.legend()
        self.graph_canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        self.graph_canvas.draw()