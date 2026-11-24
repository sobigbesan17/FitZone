import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
from gym_font import ManageFont
from gym_function_bank import MessageHandler, TimeFormatHandler


class GymMemberClassSchedulePage(GymBasePage):
    def __init__(self, member_id, location_id, fitness_dashboard_callback,
                 calculate_bmi_callback, bmi_visualisation_callback,
                 gym_meal_planner_callback, gym_workout_planner_callback,
                 view_class_schedule_callback, gym_class_booking_callback,
                 gym_class_clashes_callback):
        super().__init__()
        self.title("FitZone - Class Schedule")
        self.geometry("1200x700")
        self.member_id = member_id
        self.location_id = location_id

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)
        self.time_format_handler = TimeFormatHandler()

        self.conn = sqlite3.connect("FitZone.db")
        self.cursor = self.conn.cursor()

        self.configure(background="#f2f2f2")
        self.create_schedule_page()

    def create_schedule_page(self):
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

        tk.Label(content, text="Gym Class Schedule", font=self.manage_font.large_bold_heading_font).pack(anchor=tk.W)
        tk.Label(content, text="View the full gym class schedule for the week.",
                 font=self.manage_font.medium_letters_font).pack(anchor=tk.W, pady=(0, 10))

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for day in days:
            day_frame = tk.Frame(content, background="#333333")
            day_frame.pack(fill=tk.X, pady=5)

            tk.Label(
                day_frame, text=day,
                font=self.manage_font.medium_bold_letters_font,
                background="#333333", foreground="#FFFFFF"
            ).pack(anchor=tk.W, padx=10, pady=5)

            classes = self.get_classes_for_day(day)

            if classes:
                tree_style = ttk.Style()
                tree_style.configure("Treeview", font=self.manage_font.smaller_letters_font)

                columns = ("Class", "Type", "Start", "End", "Room", "Instructor", "Difficulty", "Spots")
                table = ttk.Treeview(content, columns=columns, show="headings", height=len(classes))
                for col in columns:
                    table.heading(col, text=col)
                    table.column(col, width=120)

                row_colors = ["#FFFFFF", "#F0F0F0"]
                for i, cls in enumerate(classes):
                    name, ctype, start, duration, room, instructor, difficulty, capacity, available = cls
                    end_time = self.time_format_handler.calculate_end_time(start, duration) if start and duration else ""
                    start_ampm = self.time_format_handler.convert_to_am_pm(start) if start else start
                    table.insert(
                        "", "end",
                        values=(name, ctype, start_ampm, end_time, room, instructor, difficulty, available),
                        tags=(row_colors[i % 2],)
                    )
                    table.tag_configure(row_colors[i % 2], background=row_colors[i % 2])
                table.pack(fill=tk.X, padx=10, pady=(0, 10))
            else:
                tk.Label(
                    content, text=f"  No classes scheduled for {day}.",
                    font=self.manage_font.smaller_letters_font
                ).pack(anchor=tk.W, padx=20)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def get_classes_for_day(self, day):
        try:
            self.cursor.execute(
                """
                SELECT gc.ClassName, gc.ClassType, cs.StartTime, cs.Duration,
                    cs.RoomNumber, gs.FirstName || ' ' || gs.LastName,
                    gc.DifficultyLevel, gc.MaxCapacity,
                    gc.MaxCapacity - (
                        SELECT COUNT(*) FROM ClassBookings cb
                        WHERE cb.ScheduleID = cs.ScheduleID AND cb.Status = 'Active'
                    ) as AvailableSpots
                FROM GymClasses gc
                JOIN ClassSchedule cs ON gc.ClassID = cs.ClassID
                LEFT JOIN GymStaff gs ON gc.InstructorID = gs.StaffID
                WHERE gc.LocationID = ? AND cs.DayOfWeek = ?
                ORDER BY cs.StartTime ASC
                """,
                (self.location_id, day)
            )
            return self.cursor.fetchall()
        except sqlite3.Error:
            return []
