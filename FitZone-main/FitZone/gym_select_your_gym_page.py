import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
from gym_font import ManageFont
from gym_function_bank import MessageHandler


class GymSelectionPage(GymBasePage):
    def __init__(self, membership_duration_callback):
        super().__init__()
        self.title("FitZone - Select Your Gym")
        self.geometry("800x600")
        self.membership_duration_callback = membership_duration_callback

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)

        self.location_id = None
        self.gym_locations = []

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

        content = tk.Frame(self.scrollable_frame)
        content.pack(fill=tk.X, pady=150, padx=60)

        ttk.Label(
            content,
            text="Select Your Gym",
            font=self.manage_font.large_bold_heading_font,
        ).pack(anchor=tk.W)

        ttk.Label(
            content,
            text="Choose a gym location to get started with your membership registration.",
            font=self.manage_font.medium_letters_font,
        ).pack(anchor=tk.W, pady=(0, 20))

        self._load_gyms()
        self._create_gym_list(content)

        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

    def _load_gyms(self):
        try:
            conn = sqlite3.connect("FitZone.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT LocationID, LocationName, Address, EmailAddress, ContactNumber, Description FROM GymLocations ORDER BY LocationName ASC"
            )
            self.gym_locations = cursor.fetchall()
            conn.close()
        except sqlite3.Error as e:
            print("Error:", e)

    def _create_gym_list(self, parent):
        self.selected_var = tk.IntVar(value=0)

        for gym in self.gym_locations:
            location_id, name, address, email, phone, description = gym

            gym_frame = tk.Frame(parent, background="#FFFFFF", relief=tk.GROOVE, bd=2)
            gym_frame.pack(fill=tk.X, padx=10, pady=10)

            rb = tk.Radiobutton(
                gym_frame,
                text=name,
                variable=self.selected_var,
                value=location_id,
                font=self.manage_font.larger_bold_letters_font,
                background="#FFFFFF",
                command=lambda lid=location_id: self._select_gym(lid),
            )
            rb.pack(anchor=tk.W, padx=10, pady=5)

            tk.Label(
                gym_frame,
                text=f"Address: {address}",
                font=self.manage_font.medium_letters_font,
                background="#FFFFFF",
            ).pack(anchor=tk.W, padx=20)

            tk.Label(
                gym_frame,
                text=f"Email: {email}   |   Phone: {phone}",
                font=self.manage_font.smaller_letters_font,
                background="#FFFFFF",
            ).pack(anchor=tk.W, padx=20, pady=(0, 5))

            if description:
                tk.Label(
                    gym_frame,
                    text=description,
                    font=self.manage_font.smaller_letters_font,
                    background="#FFFFFF",
                    wraplength=600,
                ).pack(anchor=tk.W, padx=20, pady=(0, 10))

        btn_frame = tk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=20)

        continue_btn = tk.Button(
            btn_frame,
            text="Continue",
            background="#4CAF50",
            foreground="#FFFFFF",
            font=self.manage_font.medium_bold_letters_font,
            command=self._on_continue,
        )
        continue_btn.pack(anchor=tk.CENTER, pady=10)

    def _select_gym(self, location_id):
        self.location_id = location_id

    def _on_continue(self):
        chosen = self.selected_var.get()
        if chosen == 0:
            self.message_handler.invalid_message(
                "Error: \n\n \u26A0 Please select a gym location to continue."
            )
            return
        self.location_id = chosen
        self.membership_duration_callback()

    def get_location_id(self):
        return self.location_id
