import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
from gym_font import ManageFont
from gym_function_bank import MessageHandler


class GymMembershipDurationPage(GymBasePage):
    def __init__(self, location_id, membership_package_callback):
        super().__init__()
        self.title("FitZone - Membership Duration")
        self.geometry("800x600")
        self.membership_package_callback = membership_package_callback

        self.location_id = location_id
        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)

        self.membership_duration_id = 0
        self.membership_number_of_days_id = 0
        self.package_price = 0.0

        self.configure(background="#f2f2f2")
        self._create_page()

    def _create_page(self):
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.duration_frame = tk.Frame(self.scrollable_frame)
        self.duration_frame.pack(fill=tk.X, pady=30, padx=40)

        ttk.Label(
            self.duration_frame,
            text="Choose Your Membership Duration",
            font=self.manage_font.large_bold_heading_font,
        ).pack(anchor=tk.W)

        ttk.Label(
            self.duration_frame,
            text="Select how long you would like your membership to last.",
            font=self.manage_font.medium_letters_font,
        ).pack(anchor=tk.W, pady=(0, 20))

        self._load_and_display_options()

        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

    def _load_and_display_options(self):
        try:
            conn = sqlite3.connect("FitZone.db")
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT DurationID, DurationName, NumberOfDays,
                    (SELECT MIN(Price) FROM MembershipPrices WHERE DurationID = md.DurationID) as MinPrice
                FROM MembershipDurations md
                WHERE LocationID = ?
                ORDER BY NumberOfDays ASC
                """,
                (self.location_id,),
            )
            durations = cursor.fetchall()

            cursor.execute(
                """
                SELECT NumberOfDaysID, NumberOfDays, DailyPrice
                FROM MemberDailyPrices
                WHERE LocationID = ?
                ORDER BY NumberOfDays ASC
                """,
                (self.location_id,),
            )
            daily_prices = cursor.fetchall()

            conn.close()

            all_options = []
            for dp in daily_prices:
                number_of_days_id, num_days, daily_price = dp
                total = round(num_days * daily_price, 2)
                all_options.append(("daily", number_of_days_id, 0, f"{num_days} Day(s)", total, daily_price))

            for dur in durations:
                duration_id, duration_name, num_days, min_price = dur
                if min_price is None:
                    min_price = 0.0
                all_options.append(("duration", 0, duration_id, duration_name, min_price, None))

            options_frame = tk.Frame(self.duration_frame)
            options_frame.pack(fill=tk.X)
            columns = min(3, max(2, len(all_options)))
            for i in range(columns):
                options_frame.grid_columnconfigure(i, weight=1, uniform="col")

            for index, option in enumerate(all_options):
                kind, number_of_days_id, duration_id, name, price, daily_price = option
                rounded_price = round(price, 2)
                row = index // columns
                col = index % columns

                box_frame = tk.Frame(
                    options_frame, background="#FFFFFF", relief=tk.GROOVE, bd=2, padx=12, pady=12
                )
                box_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

                if kind == "daily":
                    average_price_per_day = round(daily_price, 2)
                    tk.Label(
                        box_frame,
                        text=name,
                        font=self.manage_font.large_bold_heading_font,
                        background="#FFFFFF",
                    ).pack(anchor=tk.CENTER)
                    tk.Label(
                        box_frame,
                        text=f"${average_price_per_day} per day",
                        font=self.manage_font.medium_bold_letters_font,
                        background="#FFFFFF",
                        foreground="#82B366",
                    ).pack(anchor=tk.CENTER)
                    tk.Label(
                        box_frame,
                        text=f"Price: ${rounded_price}",
                        font=self.manage_font.large_bold_letters_font,
                        background="#FFFFFF",
                    ).pack(anchor=tk.CENTER)
                    tk.Button(
                        box_frame,
                        text="Choose",
                        command=lambda nid=number_of_days_id, n=name, p=price: self.select_package(nid, 0, n, p),
                        font=self.manage_font.medium_letters_font,
                        background="#333333",
                        foreground="#FFFFFF",
                    ).pack(anchor=tk.E)
                else:
                    from_price = price
                    tk.Label(
                        box_frame,
                        text=name,
                        font=self.manage_font.large_bold_heading_font,
                        width=35,
                        background="#FFFFFF",
                    ).pack(anchor=tk.W)
                    tk.Label(
                        box_frame,
                        text=f"From ${from_price}",
                        font=self.manage_font.large_bold_letters_font,
                        background="#FFFFFF",
                    ).pack(anchor=tk.W)
                    tk.Button(
                        box_frame,
                        text="Choose",
                        command=lambda did=duration_id, n=name, p=from_price: self.select_package(0, did, n, p),
                        font=self.manage_font.medium_letters_font,
                        background="#333333",
                        foreground="#FFFFFF",
                    ).pack(anchor=tk.E)

                col += 1

        except sqlite3.Error as e:
            print("Error:", e)
            tk.Label(
                self.duration_frame,
                text="No membership options available for this location.",
                font=self.manage_font.medium_letters_font,
            ).pack()

            continue_btn = tk.Button(
                self.duration_frame,
                text="Continue",
                background="#4CAF50",
                foreground="#FFFFFF",
                font=self.manage_font.medium_bold_letters_font,
                command=lambda: self.select_package(0, 0, "No Package", 0),
            )
            continue_btn.pack(pady=10)

    def select_package(self, number_of_days_id, duration_id, package_name, package_price):
        try:
            self.box_frame.destroy()
        except Exception:
            pass

        self.membership_number_of_days_id = number_of_days_id
        self.membership_duration_id = duration_id
        self.package_price = package_price

        self.box_frame = tk.Frame(self.duration_frame, background="#333333")
        self.box_frame.pack(padx=10, pady=10)

        tk.Label(
            self.box_frame,
            text=f"Your selected membership plan: {package_name}",
            font=self.manage_font.large_bold_letters_font,
            background="#333333",
            foreground="#FFFFFF",
        ).pack(anchor=tk.W)

        tk.Label(
            self.box_frame,
            text=f"From ${package_price}",
            font=self.manage_font.medium_letters_font,
            background="#333333",
            foreground="#FFFFFF",
        ).pack(anchor=tk.W)

        self.continue_button = tk.Button(
            self.box_frame,
            text="Continue",
            width=200,
            background="#4CAF50",
            foreground="#000000",
            font=self.manage_font.small_bold_heading_font,
        )
        self.continue_button.pack(anchor=tk.CENTER)
        self.continue_button.bind(
            "<Button-1>", lambda event, func=self.membership_package_callback: func()
        )

    def get_membership_duration_id(self):
        return self.membership_duration_id

    def get_membership_number_of_days_id(self):
        return self.membership_number_of_days_id

    def get_membership_price(self):
        return self.package_price
