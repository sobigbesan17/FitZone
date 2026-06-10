import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
from gym_font import ManageFont
from gym_function_bank import MessageHandler


class GymViewTeamPage(GymBasePage):
    def __init__(self, location_id, home_callback):
        super().__init__()
        self.title("FitZone - Our Team")
        self.geometry("1000x700")
        self.location_id = location_id
        self.home_callback = home_callback

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)

        self.conn = sqlite3.connect("FitZone.db")
        self.cursor = self.conn.cursor()

        self.configure(background="#f2f2f2")
        self.create_team_page()

    def create_team_page(self):
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

        tk.Label(content, text="Meet Our Team", font=self.manage_font.large_bold_heading_font).pack(anchor=tk.W, pady=(20, 5))
        tk.Label(content, text="Our expert trainers and instructors are dedicated to helping you reach your fitness goals.",
                 font=self.manage_font.medium_letters_font).pack(anchor=tk.W, pady=(0, 20))

        self.load_team_members(content)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def load_team_members(self, parent):
        try:
            query = """
                SELECT FirstName, LastName, Role, Bio, ImagePath
                FROM GymStaff
                WHERE LocationID = ?
                ORDER BY LastName ASC
            """
            self.cursor.execute(query, (self.location_id,))
            staff = self.cursor.fetchall()

            if not staff:
                tk.Label(
                    parent,
                    text="No team members listed for this gym location.",
                    font=self.manage_font.medium_letters_font
                ).pack(pady=20)
                return

            grid_frame = tk.Frame(parent, background="#f2f2f2")
            grid_frame.pack(fill=tk.X)

            for i, (first_name, last_name, role, bio, image_path) in enumerate(staff):
                col = i % 3
                row = i // 3

                card = tk.Frame(grid_frame, background="#FFFFFF", relief=tk.GROOVE, bd=1, padx=15, pady=15)
                card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

                icon_label = tk.Label(
                    card, text="\U0001F464",
                    font=("Helvetica", 36), background="#FFFFFF"
                )
                icon_label.pack()

                tk.Label(
                    card, text=f"{first_name} {last_name}",
                    font=self.manage_font.medium_bold_letters_font,
                    background="#FFFFFF"
                ).pack()

                tk.Label(
                    card, text=role or "Instructor",
                    font=self.manage_font.smaller_letters_font,
                    background="#FFFFFF", foreground="#D11A17"
                ).pack()

                if bio:
                    tk.Label(
                        card, text=bio,
                        font=self.manage_font.smaller_letters_font,
                        background="#FFFFFF", foreground="#555555",
                        wraplength=250
                    ).pack(pady=(5, 0))

        except sqlite3.Error as e:
            self.message_handler.invalid_message(f"Error loading team: {e}")
