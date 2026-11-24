import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
from gym_font import ManageFont
from gym_function_bank import MessageHandler, TimeFormatHandler


class GymClassReservationPage(GymBasePage):
    def __init__(self, member_id, location_id, fitness_dashboard_callback,
                 calculate_bmi_callback, bmi_visualisation_callback,
                 gym_meal_planner_callback, gym_workout_planner_callback,
                 view_class_schedule_callback, gym_class_booking_callback,
                 gym_class_clashes_callback):
        super().__init__()
        self.title("FitZone - My Class Reservations")
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
        self.create_reservations_page()

    def create_reservations_page(self):
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

        tk.Label(content, text="My Class Reservations", font=self.manage_font.large_bold_heading_font).pack(anchor=tk.W)
        tk.Label(content, text="View and manage your gym class bookings.",
                 font=self.manage_font.medium_letters_font).pack(anchor=tk.W, pady=(0, 20))

        tree_style = ttk.Style()
        tree_style.configure("Treeview", font=self.manage_font.smaller_letters_font)
        tree_style.configure("Treeview.Heading", font=self.manage_font.medium_bold_letters_font)

        columns = ("Booking ID", "Class", "Type", "Day", "Start Time", "End Time", "Room", "Instructor", "Booking Date", "Status")
        self.table = ttk.Treeview(content, columns=columns, show="headings", height=12)
        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=90)

        self.table.pack(fill=tk.X, pady=10)
        self.table.bind("<<TreeviewSelect>>", self.on_booking_select)

        self.load_reservations()

        button_frame = tk.Frame(content)
        button_frame.pack(fill=tk.X, pady=10)

        self.cancel_btn = tk.Button(
            button_frame, text="Cancel Selected Booking",
            font=self.manage_font.medium_bold_letters_font,
            background="#D11A17", foreground="#FFFFFF",
            state=tk.DISABLED, command=self.cancel_booking
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=10)

        tk.Button(
            button_frame, text="Refresh",
            font=self.manage_font.medium_letters_font,
            background="#333333", foreground="#FFFFFF",
            command=self.load_reservations
        ).pack(side=tk.LEFT, padx=5)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def load_reservations(self):
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            self.cursor.execute(
                """
                SELECT cb.BookingID, gc.ClassName, gc.ClassType, cs.DayOfWeek,
                    cs.StartTime, cs.Duration, cs.RoomNumber,
                    gs.FirstName || ' ' || gs.LastName, cb.BookingDate, cb.Status
                FROM ClassBookings cb
                JOIN ClassSchedule cs ON cb.ScheduleID = cs.ScheduleID
                JOIN GymClasses gc ON cs.ClassID = gc.ClassID
                LEFT JOIN GymStaff gs ON gc.InstructorID = gs.StaffID
                WHERE cb.MemberID = ?
                ORDER BY cb.BookingDate DESC
                """,
                (self.member_id,)
            )
            bookings = self.cursor.fetchall()

            self.booking_ids = {}
            row_colors = {
                "Active": "#D5F5E3",
                "Cancelled": "#FADBD8",
                "Completed": "#D6EAF8",
            }
            for booking in bookings:
                booking_id, name, ctype, day, start, duration, room, instructor, booking_date, status = booking
                end_time = self.time_format_handler.calculate_end_time(start, duration) if start and duration else ""
                start_ampm = self.time_format_handler.convert_to_am_pm(start) if start else start
                color = row_colors.get(status, "#FFFFFF")
                row_id = self.table.insert(
                    "", "end",
                    values=(booking_id, name, ctype, day, start_ampm, end_time, room, instructor, booking_date, status),
                    tags=(color,)
                )
                self.table.tag_configure(color, background=color)
                self.booking_ids[row_id] = (booking_id, name, status)

        except sqlite3.Error as e:
            self.message_handler.invalid_message(f"Error loading reservations: {e}")

    def on_booking_select(self, event):
        selected = self.table.selection()
        if selected:
            row_id = selected[0]
            if row_id in self.booking_ids:
                self.selected_booking_id, self.selected_class_name, status = self.booking_ids[row_id]
                if status == "Active":
                    self.cancel_btn.config(state=tk.NORMAL)
                else:
                    self.cancel_btn.config(state=tk.DISABLED)

    def cancel_booking(self):
        if not self.selected_booking_id:
            self.message_handler.invalid_message("Error: \n\n \u26A0 Please select a booking to cancel.")
            return

        try:
            self.cursor.execute(
                "UPDATE ClassBookings SET Status = 'Cancelled' WHERE BookingID = ? AND MemberID = ?",
                (self.selected_booking_id, self.member_id)
            )
            self.conn.commit()
            self.message_handler.success_message(
                f"Success: \n\n \u2705 Booking for '{self.selected_class_name}' has been cancelled."
            )
            self.cancel_btn.config(state=tk.DISABLED)
            self.selected_booking_id = None
            self.load_reservations()
        except sqlite3.Error as e:
            self.message_handler.invalid_message(f"Error: \n\n \u26A0 Could not cancel booking: {e}")
