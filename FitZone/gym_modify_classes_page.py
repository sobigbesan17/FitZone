import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
from gym_font import ManageFont
from gym_function_bank import MessageHandler, TimeFormatHandler, ReadText


class LeaveClassPage(GymBasePage):
    def __init__(self, member_id, location_id, fitness_dashboard_callback,
                 calculate_bmi_callback, bmi_visualisation_callback,
                 gym_meal_planner_callback, gym_workout_planner_callback,
                 view_class_schedule_callback, gym_class_booking_callback,
                 gym_class_clashes_callback):
        super().__init__()
        self.title("FitZone - Leave a Class")
        self.geometry("1000x700")
        self.member_id = member_id
        self.location_id = location_id

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)
        self.time_format_handler = TimeFormatHandler()

        self.conn = sqlite3.connect("FitZone.db")
        self.cursor = self.conn.cursor()

        self.selected_booking_id = None
        self.selected_class_name = None

        self.configure(background="#f2f2f2")
        self.create_leave_class_page()

    def create_leave_class_page(self):
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

        tk.Label(content, text="Leave a Class", font=self.manage_font.large_bold_heading_font).pack(anchor=tk.W)
        tk.Label(content, text="Select a class booking below to leave or cancel it.",
                 font=self.manage_font.medium_letters_font).pack(anchor=tk.W, pady=(0, 10))

        try:
            read_text = ReadText("gym_leaving_class.txt")
            leaving_info = read_text.extract_description("Leaving Class Information:")
            if leaving_info and leaving_info != "Text not found":
                info_frame = tk.Frame(content, background="#FFF3CD")
                info_frame.pack(fill=tk.X, pady=5)
                tk.Label(
                    info_frame, text=leaving_info,
                    font=self.manage_font.smaller_letters_font,
                    background="#FFF3CD", wraplength=800
                ).pack(padx=10, pady=5)
        except Exception:
            pass

        tree_style = ttk.Style()
        tree_style.configure("Treeview", font=self.manage_font.smaller_letters_font)
        tree_style.configure("Treeview.Heading", font=self.manage_font.medium_bold_letters_font)

        columns = ("Booking ID", "Class", "Day", "Start Time", "Room", "Booking Date", "Status")
        self.table = ttk.Treeview(content, columns=columns, show="headings", height=10)
        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=120)

        self.table.pack(fill=tk.X, pady=10)
        self.table.bind("<<TreeviewSelect>>", self.on_booking_select)

        self.load_active_bookings()

        button_frame = tk.Frame(content)
        button_frame.pack(fill=tk.X, pady=10)

        self.leave_btn = tk.Button(
            button_frame, text="Leave Selected Class",
            font=self.manage_font.medium_bold_letters_font,
            background="#D11A17", foreground="#FFFFFF",
            state=tk.DISABLED, command=self.leave_class
        )
        self.leave_btn.pack(side=tk.LEFT, padx=10)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def load_active_bookings(self):
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            self.cursor.execute(
                """
                SELECT cb.BookingID, gc.ClassName, cs.DayOfWeek, cs.StartTime,
                    cs.RoomNumber, cb.BookingDate, cb.Status
                FROM ClassBookings cb
                JOIN ClassSchedule cs ON cb.ScheduleID = cs.ScheduleID
                JOIN GymClasses gc ON cs.ClassID = gc.ClassID
                WHERE cb.MemberID = ? AND cb.Status = 'Active'
                ORDER BY cs.DayOfWeek, cs.StartTime
                """,
                (self.member_id,)
            )
            bookings = self.cursor.fetchall()

            self.booking_ids = {}
            row_colors = ["#D5F5E3", "#FFFFFF"]
            for i, booking in enumerate(bookings):
                booking_id, name, day, start, room, booking_date, status = booking
                start_ampm = self.time_format_handler.convert_to_am_pm(start) if start else start
                row_id = self.table.insert(
                    "", "end",
                    values=(booking_id, name, day, start_ampm, room, booking_date, status),
                    tags=(row_colors[i % 2],)
                )
                self.table.tag_configure(row_colors[i % 2], background=row_colors[i % 2])
                self.booking_ids[row_id] = (booking_id, name)

        except sqlite3.Error as e:
            self.message_handler.invalid_message(f"Error loading bookings: {e}")

    def on_booking_select(self, event):
        selected = self.table.selection()
        if selected:
            row_id = selected[0]
            if row_id in self.booking_ids:
                self.selected_booking_id, self.selected_class_name = self.booking_ids[row_id]
                self.leave_btn.config(state=tk.NORMAL)

    def leave_class(self):
        if not self.selected_booking_id:
            self.message_handler.invalid_message("Error: \n\n \u26A0 Please select a class to leave.")
            return

        try:
            self.cursor.execute(
                "UPDATE ClassBookings SET Status = 'Cancelled' WHERE BookingID = ? AND MemberID = ?",
                (self.selected_booking_id, self.member_id)
            )
            self.conn.commit()
            self.message_handler.success_message(
                f"Success: \n\n \u2705 You have successfully left '{self.selected_class_name}'."
            )
            self.leave_btn.config(state=tk.DISABLED)
            self.selected_booking_id = None
            self.load_active_bookings()
        except sqlite3.Error as e:
            self.message_handler.invalid_message(f"Error: \n\n \u26A0 Could not leave class: {e}")
