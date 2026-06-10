import sqlite3
import tkinter as tk
from tkinter import ttk
from gym_page_base import GymBasePage
from gym_font import ManageFont
from gym_function_bank import MessageHandler, TimeFormatHandler
import datetime


class GymClassBookingPage(GymBasePage):
    def __init__(self, member_id, location_id, fitness_dashboard_callback,
                 calculate_bmi_callback, bmi_visualisation_callback,
                 gym_meal_planner_callback, gym_workout_planner_callback,
                 view_class_schedule_callback, gym_class_booking_callback,
                 gym_class_clashes_callback):
        super().__init__()
        self.title("FitZone - Book a Class")
        self.geometry("1000x700")
        self.member_id = member_id
        self.location_id = location_id
        self.fitness_dashboard_callback = fitness_dashboard_callback
        self.calculate_bmi_callback = calculate_bmi_callback
        self.bmi_visualisation_callback = bmi_visualisation_callback
        self.gym_meal_planner_callback = gym_meal_planner_callback
        self.gym_workout_planner_callback = gym_workout_planner_callback
        self.view_class_schedule_callback = view_class_schedule_callback
        self.gym_class_booking_callback = gym_class_booking_callback
        self.gym_class_clashes_callback = gym_class_clashes_callback

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)
        self.time_format_handler = TimeFormatHandler()

        self.conn = sqlite3.connect("FitZone.db")
        self.cursor = self.conn.cursor()

        self.selected_schedule_id = None
        self.selected_class_name = None

        self.configure(background="#f2f2f2")
        self.create_booking_page()

    def create_booking_page(self):
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

        tk.Label(content, text="Book a Gym Class", font=self.manage_font.large_bold_heading_font).pack(anchor=tk.W)
        tk.Label(content, text="Select a class and time slot to make a booking.",
                 font=self.manage_font.medium_letters_font).pack(anchor=tk.W, pady=(0, 20))

        filter_frame = tk.Frame(content)
        filter_frame.pack(fill=tk.X, pady=10)

        tk.Label(filter_frame, text="Filter by Day:", font=self.manage_font.medium_bold_letters_font).grid(row=0, column=0, padx=5)
        days = ["All", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.day_var = tk.StringVar(value="All")
        day_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.day_var,
            values=days,
            state="readonly",
            width=15,
            font=self.manage_font.medium_letters_font,
        )
        day_combo.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Filter by Class Type:", font=self.manage_font.medium_bold_letters_font).grid(row=0, column=2, padx=5)
        self.class_type_var = tk.StringVar(value="All")
        self.class_types = ["All"] + self.get_class_types()
        class_type_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.class_type_var,
            values=self.class_types,
            state="readonly",
            width=20,
            font=self.manage_font.medium_letters_font,
        )
        class_type_combo.grid(row=0, column=3, padx=5)

        tk.Button(
            filter_frame, text="Apply Filter",
            font=self.manage_font.medium_letters_font,
            background="#333333", foreground="#FFFFFF",
            command=lambda: self.load_classes(table)
        ).grid(row=0, column=4, padx=10)

        tree_style = ttk.Style()
        tree_style.configure("Treeview", font=self.manage_font.smaller_letters_font)
        tree_style.configure("Treeview.Heading", font=self.manage_font.medium_bold_letters_font)

        columns = ("Class", "Type", "Day", "Start Time", "End Time", "Duration", "Room", "Instructor", "Difficulty", "Available Spots")
        table = ttk.Treeview(content, columns=columns, show="headings", height=12)
        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=100)

        table.pack(fill=tk.X, pady=10)
        table.bind("<<TreeviewSelect>>", lambda e: self.on_class_select(e, table))

        self.load_classes(table)

        button_frame = tk.Frame(content)
        button_frame.pack(fill=tk.X, pady=10)

        self.book_btn = tk.Button(
            button_frame, text="Book Selected Class",
            font=self.manage_font.medium_bold_letters_font,
            background="#4CAF50", foreground="#FFFFFF",
            state=tk.DISABLED, command=self.book_class
        )
        self.book_btn.pack(side=tk.LEFT, padx=10)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def get_class_types(self):
        try:
            self.cursor.execute(
                "SELECT DISTINCT ClassType FROM GymClasses WHERE LocationID = ?",
                (self.location_id,)
            )
            return [row[0] for row in self.cursor.fetchall() if row[0]]
        except Exception:
            return []

    def load_classes(self, table):
        for item in table.get_children():
            table.delete(item)

        try:
            query = """
                SELECT gc.ClassName, gc.ClassType, cs.DayOfWeek, cs.StartTime,
                    cs.Duration, cs.RoomNumber, gs.FirstName || ' ' || gs.LastName,
                    gc.DifficultyLevel, gc.MaxCapacity,
                    cs.ScheduleID, gc.MaxCapacity - (
                        SELECT COUNT(*) FROM ClassBookings cb
                        WHERE cb.ScheduleID = cs.ScheduleID AND cb.Status = 'Active'
                    ) as AvailableSpots
                FROM GymClasses gc
                JOIN ClassSchedule cs ON gc.ClassID = cs.ClassID
                LEFT JOIN GymStaff gs ON gc.InstructorID = gs.StaffID
                WHERE gc.LocationID = ?
            """
            params = [self.location_id]

            if self.day_var.get() != "All":
                query += " AND cs.DayOfWeek = ?"
                params.append(self.day_var.get())

            if self.class_type_var.get() != "All":
                query += " AND gc.ClassType = ?"
                params.append(self.class_type_var.get())

            self.cursor.execute(query, params)
            classes = self.cursor.fetchall()

            row_colors = ["#FFFFFF", "#F0F0F0"]
            self.schedule_ids = {}
            for i, cls in enumerate(classes):
                name, ctype, day, start, duration, room, instructor, difficulty, capacity, schedule_id, available = cls
                end_time = self.time_format_handler.calculate_end_time(start, duration) if start and duration else ""
                start_ampm = self.time_format_handler.convert_to_am_pm(start) if start else start

                row_id = table.insert(
                    "", "end",
                    values=(name, ctype, day, start_ampm, end_time, duration, room, instructor, difficulty, available),
                    tags=(row_colors[i % 2],)
                )
                table.tag_configure(row_colors[i % 2], background=row_colors[i % 2])
                self.schedule_ids[row_id] = (schedule_id, name)

        except sqlite3.Error as e:
            self.message_handler.invalid_message(f"Error loading classes: {e}")

    def on_class_select(self, event, table):
        selected = table.selection()
        if selected:
            row_id = selected[0]
            if row_id in self.schedule_ids:
                self.selected_schedule_id, self.selected_class_name = self.schedule_ids[row_id]
                self.book_btn.config(state=tk.NORMAL)

    def book_class(self):
        if not self.selected_schedule_id:
            self.message_handler.invalid_message("Error: \n\n \u26A0 Please select a class to book.")
            return

        try:
            self.cursor.execute(
                "SELECT BookingID FROM ClassBookings WHERE MemberID = ? AND ScheduleID = ? AND Status = 'Active'",
                (self.member_id, self.selected_schedule_id)
            )
            existing = self.cursor.fetchone()

            if existing:
                self.message_handler.invalid_message(
                    "Error: \n\n \u26A0 You have already booked this class."
                )
                return

            self.cursor.execute(
                "SELECT gc.MaxCapacity, COUNT(cb.BookingID) FROM GymClasses gc "
                "JOIN ClassSchedule cs ON gc.ClassID = cs.ClassID "
                "LEFT JOIN ClassBookings cb ON cs.ScheduleID = cb.ScheduleID AND cb.Status = 'Active' "
                "WHERE cs.ScheduleID = ? GROUP BY gc.MaxCapacity",
                (self.selected_schedule_id,)
            )
            result = self.cursor.fetchone()
            if result and result[0] and result[1] >= result[0]:
                self.message_handler.invalid_message(
                    "Error: \n\n \u26A0 This class is full. No available spots."
                )
                return

            booking_date = datetime.date.today()
            self.cursor.execute(
                "INSERT INTO ClassBookings (MemberID, ScheduleID, BookingDate, Status) VALUES (?, ?, ?, 'Active')",
                (self.member_id, self.selected_schedule_id, booking_date)
            )
            self.conn.commit()
            self.message_handler.success_message(
                f"Success: \n\n \u2705 Successfully booked '{self.selected_class_name}'!"
            )
            self.book_btn.config(state=tk.DISABLED)
            self.selected_schedule_id = None

        except sqlite3.Error as e:
            self.message_handler.invalid_message(f"Error: \n\n \u26A0 Could not book class: {e}")
