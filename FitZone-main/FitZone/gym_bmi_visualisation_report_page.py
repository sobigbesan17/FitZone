import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
import matplotlib
import matplotlib.figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from gym_font import ManageFont
from gym_function_bank import MessageHandler
from scipy.interpolate import make_interp_spline


class BMIVisualisationReportPage(GymBasePage):
    def __init__(self, member_id, fitness_dashboard_callback, calculate_bmi_callback,
                 bmi_visualisation_callback, gym_meal_planner_callback,
                 gym_workout_planner_callback, view_class_schedule_callback,
                 gym_class_booking_callback, gym_class_clashes_callback):
        super().__init__()
        self.title("BMI Visualisation Report")
        self.member_id = member_id

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)

        self.conn = sqlite3.connect("FitZone.db")
        self.cursor = self.conn.cursor()

        self.bmi_data = []
        self.load_bmi_data()
        self.create_bmi_report_page()

    def load_bmi_data(self):
        try:
            self.cursor.execute(
                """SELECT DateRecorded, BMI, BMICategory, Weight, Height, MeasurementSystem
                   FROM BMIRecords WHERE MemberID = ? ORDER BY DateRecorded ASC""",
                (self.member_id,)
            )
            self.bmi_data = self.cursor.fetchall()
        except sqlite3.Error as e:
            print("Error:", e)
            self.bmi_data = []

    def create_bmi_report_page(self):
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

        tk.Label(content, text="BMI Visualisation Report", font=self.manage_font.large_bold_heading_font).pack(anchor=tk.W)
        tk.Label(content, text="Your BMI history and progress over time.", font=self.manage_font.medium_letters_font).pack(anchor=tk.W, pady=(0, 20))

        if not self.bmi_data:
            tk.Label(
                content,
                text="No BMI records found. Please calculate your BMI first.",
                font=self.manage_font.medium_letters_font
            ).pack(pady=20)
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            return

        self.create_bmi_table(content)
        self.create_bmi_graph(content)
        self.create_bmi_category_distribution(content)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def create_bmi_table(self, parent):
        tk.Label(parent, text="BMI Records:", font=self.manage_font.medium_bold_letters_font).pack(anchor=tk.W, pady=(10, 0))

        tree_style = ttk.Style()
        tree_style.configure("Treeview", font=self.manage_font.smaller_letters_font)
        tree_style.configure("Treeview.Heading", font=self.manage_font.medium_bold_letters_font)

        bmi_table = ttk.Treeview(
            parent,
            columns=("Date", "BMI", "Category", "Weight", "Height", "System"),
            show="headings", height=8
        )
        for col, text in [
            ("Date", "Date"), ("BMI", "BMI"), ("Category", "Category"),
            ("Weight", "Weight"), ("Height", "Height"), ("System", "Measurement System")
        ]:
            bmi_table.heading(col, text=text)
            bmi_table.column(col, width=130)

        row_colors = ["#D6EAF8", "#FFFFFF"]
        for i, record in enumerate(self.bmi_data):
            date, bmi, category, weight, height, system = record
            bmi_table.insert(
                "", "end",
                values=(date, f"{bmi:.2f}", category, weight, height, system),
                tags=(row_colors[i % 2],)
            )
            bmi_table.tag_configure(row_colors[i % 2], background=row_colors[i % 2])

        bmi_table.pack(fill=tk.X, pady=10)

    def create_bmi_graph(self, parent):
        if len(self.bmi_data) < 2:
            tk.Label(parent, text="Need at least 2 BMI records to show progress graph.",
                     font=self.manage_font.smaller_letters_font).pack()
            return

        dates = [record[0] for record in self.bmi_data]
        bmis = [record[1] for record in self.bmi_data]

        fig = matplotlib.figure.Figure(figsize=(12, 4), dpi=100)
        ax = fig.add_subplot(111)
        fig.patch.set_facecolor("#30257D")
        ax.set_facecolor("#30257D")

        x = np.arange(len(dates))
        y = np.array(bmis, dtype=float)

        if len(x) >= 2:
            k = min(len(x) - 1, 3)
            x_new = np.linspace(x.min(), x.max(), 300)
            spl = make_interp_spline(x, y, k=k)
            y_new = spl(x_new)
            ax.plot(x_new, y_new, color="#FFFFFF", label="BMI Trend")

        ax.scatter(x, y, color="#FFD700", zorder=5, label="BMI Values")

        ax.axhline(y=18.5, color="#00BFFF", linestyle="--", alpha=0.7, label="Underweight (18.5)")
        ax.axhline(y=24.9, color="#32CD32", linestyle="--", alpha=0.7, label="Normal (24.9)")
        ax.axhline(y=29.9, color="#FFA500", linestyle="--", alpha=0.7, label="Overweight (29.9)")

        for spine in ax.spines.values():
            spine.set_color("white")
        ax.tick_params(axis="x", colors="white")
        ax.tick_params(axis="y", colors="white")
        ax.set_xlabel("Date", color="white")
        ax.set_ylabel("BMI", color="white")
        ax.set_title("BMI Progress Over Time", color="white")
        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=45, ha="right", fontsize=8, color="white")
        ax.legend(facecolor="#333333", labelcolor="white")

        graph_canvas = FigureCanvasTkAgg(fig, master=parent)
        graph_canvas.draw()
        graph_canvas.get_tk_widget().pack(pady=20)

    def create_bmi_category_distribution(self, parent):
        from collections import Counter
        categories = [record[2] for record in self.bmi_data]
        category_counts = Counter(categories)

        category_colors = {
            "Underweight": "#00BFFF",
            "Normal Weight": "#32CD32",
            "Overweight": "#FFA500",
            "Obese (Class 1)": "#FF4500",
            "Obese (Class 2)": "#DC143C",
            "Obese (Class 3)": "#8B0000",
        }

        fig = matplotlib.figure.Figure(figsize=(6, 4), dpi=100)
        fig.patch.set_facecolor("#333333")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#333333")

        labels = list(category_counts.keys())
        sizes = list(category_counts.values())
        colors = [category_colors.get(label, "#AAAAAA") for label in labels]

        ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90,
               textprops={"color": "white"})
        ax.set_title("BMI Category Distribution", color="white")

        pie_canvas = FigureCanvasTkAgg(fig, master=parent)
        pie_canvas.draw()
        pie_canvas.get_tk_widget().pack(pady=10)
