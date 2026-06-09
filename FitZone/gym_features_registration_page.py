import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
from gym_font import ManageFont
from gym_function_bank import MessageHandler


class GymFeaturesPage(GymBasePage):
    def __init__(self, location_id, home_callback):
        super().__init__()
        self.title("FitZone - Gym Features")
        self.geometry("1000x700")
        self.location_id = location_id
        self.home_callback = home_callback

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)

        self.conn = sqlite3.connect("FitZone.db")
        self.cursor = self.conn.cursor()

        self.configure(background="#f2f2f2")
        self.create_features_page()

    def create_features_page(self):
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

        tk.Label(content, text="Gym Features", font=self.manage_font.large_bold_heading_font).pack(anchor=tk.W, pady=(20, 5))
        tk.Label(content, text="Explore the world-class features and facilities available at your gym.",
                 font=self.manage_font.medium_letters_font).pack(anchor=tk.W, pady=(0, 20))

        self.load_features(content)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def load_features(self, parent):
        try:
            query = """
                SELECT FeatureName, FeatureDescription, ImagePath
                FROM GymFeatures
                WHERE LocationID = ?
                ORDER BY FeatureName ASC
            """
            self.cursor.execute(query, (self.location_id,))
            features = self.cursor.fetchall()

            if not features:
                tk.Label(
                    parent,
                    text="No features available for this gym location.",
                    font=self.manage_font.medium_letters_font
                ).pack(pady=20)
                return

            for i, (name, description, image_path) in enumerate(features):
                feature_frame = tk.Frame(parent, background="#FFFFFF", relief=tk.GROOVE, bd=1)
                feature_frame.pack(fill=tk.X, pady=10)

                bg = "#F0F8FF" if i % 2 == 0 else "#FFF8F0"

                header_frame = tk.Frame(feature_frame, background=bg)
                header_frame.pack(fill=tk.X, padx=10, pady=5)

                tk.Label(
                    header_frame, text=name,
                    font=self.manage_font.larger_bold_letters_font,
                    background=bg
                ).pack(anchor=tk.W)

                if description:
                    tk.Label(
                        feature_frame, text=description,
                        font=self.manage_font.medium_letters_font,
                        background="#FFFFFF", wraplength=800
                    ).pack(anchor=tk.W, padx=20, pady=(0, 10))

        except sqlite3.Error as e:
            self.message_handler.invalid_message(f"Error loading features: {e}")
