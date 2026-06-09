import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
from gym_font import ManageFont
from gym_function_bank import MessageHandler, TimeFormatHandler
import datetime


class GymClassClashesPage(GymBasePage):
    def __init__(self, member_id, location_id, fitness_dashboard_callback,
                 calculate_bmi_callback, bmi_visualisation_callback,
                 gym_meal_planner_callback, gym_workout_planner_callback,
                 view_class_schedule_callback, gym_class_booking_callback,
                 gym_class_clashes_callback):
        super().__init__()
        self.title("FitZone - Class Clashes")
        self.geometry("1000x700")
        self.member_id = member_id
        self.location_id = location_id

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)
        self.time_format_handler = TimeFormatHandler()

        self.conn = sqlite3.connect("FitZone.db")
        self.cursor = self.conn.cursor()

        self.configure(background="#f2f2f2")
        self.create_clashes_page()

    def create_clashes_page(self):
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

        tk.Label(content, text="Class Clashes", font=self.manage_font.large_bold_heading_font).pack(anchor=tk.W)
        tk.Label(content, text="The following are your class bookings that have scheduling conflicts.",
                 font=self.manage_font.medium_letters_font).pack(anchor=tk.W, pady=(0, 20))

        clashes = self.detect_clashes()

        if not clashes:
            tk.Label(
                content,
                text="\u2705 No class clashes detected! Your schedule is clear.",
                font=self.manage_font.medium_bold_letters_font,
                foreground="#4CAF50"
            ).pack(pady=20)
        else:
            tk.Label(
                content,
                text=f"\u26A0 {len(clashes)} clash(es) detected:",
                font=self.manage_font.medium_bold_letters_font,
                foreground="#D11A17"
            ).pack(anchor=tk.W, pady=(0, 10))

            tree_style = ttk.Style()
            tree_style.configure("Treeview", font=self.manage_font.smaller_letters_font)
            tree_style.configure("Treeview.Heading", font=self.manage_font.medium_bold_letters_font)

            columns = ("Class A", "Day", "Start A", "End A", "Class B", "Start B", "End B")
            clash_table = ttk.Treeview(content, columns=columns, show="headings", height=len(clashes))
            for col in columns:
                clash_table.heading(col, text=col)
                clash_table.column(col, width=130)

            for clash in clashes:
                clash_table.insert("", "end", values=clash, tags=("#FADBD8",))
                clash_table.tag_configure("#FADBD8", background="#FADBD8")

            clash_table.pack(fill=tk.X, pady=10)

            tk.Label(
                content,
                text="Please resolve clashes by cancelling one of the conflicting bookings in 'My Reservations'.",
                font=self.manage_font.smaller_letters_font, foreground="#555555"
            ).pack(anchor=tk.W, pady=5)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def detect_clashes(self):
        clashes = []
        try:
            self.cursor.execute(
                """
                SELECT gc.ClassName, cs.DayOfWeek, cs.StartTime, cs.Duration, cb.BookingID
                FROM ClassBookings cb
                JOIN ClassSchedule cs ON cb.ScheduleID = cs.ScheduleID
                JOIN GymClasses gc ON cs.ClassID = gc.ClassID
                WHERE cb.MemberID = ? AND cb.Status = 'Active'
                ORDER BY cs.DayOfWeek, cs.StartTime
                """,
                (self.member_id,)
            )
            bookings = self.cursor.fetchall()

            for i in range(len(bookings)):
                for j in range(i + 1, len(bookings)):
                    name_a, day_a, start_a, dur_a, id_a = bookings[i]
                    name_b, day_b, start_b, dur_b, id_b = bookings[j]

                    if day_a != day_b:
                        continue

                    try:
                        fmt = "%H:%M"
                        start_a_dt = datetime.datetime.strptime(start_a, fmt)
                        end_a_dt = start_a_dt + self._parse_duration(dur_a)
                        start_b_dt = datetime.datetime.strptime(start_b, fmt)
                        end_b_dt = start_b_dt + self._parse_duration(dur_b)

                        if start_a_dt < end_b_dt and end_a_dt > start_b_dt:
                            clashes.append((
                                name_a, day_a,
                                start_a_dt.strftime("%I:%M %p"),
                                end_a_dt.strftime("%I:%M %p"),
                                name_b,
                                start_b_dt.strftime("%I:%M %p"),
                                end_b_dt.strftime("%I:%M %p"),
                            ))
                    except Exception:
                        pass

        except sqlite3.Error as e:
            print("Error detecting clashes:", e)

        return clashes

    def _parse_duration(self, duration_str):
        try:
            parts = duration_str.split(":")
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
            return datetime.timedelta(hours=hours, minutes=minutes)
        except Exception:
            return datetime.timedelta(hours=1)
