import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
from gym_font import ManageFont
from gym_function_bank import MessageHandler
import datetime


class GymReviewsPage(GymBasePage):
    def __init__(self, member_id, location_id, home_callback):
        super().__init__()
        self.title("FitZone - Reviews")
        self.geometry("1000x700")
        self.member_id = member_id
        self.location_id = location_id
        self.home_callback = home_callback

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)

        self.conn = sqlite3.connect("FitZone.db")
        self.cursor = self.conn.cursor()

        self.configure(background="#f2f2f2")
        self.create_reviews_page()

    def create_reviews_page(self):
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

        tk.Label(content, text="Gym Reviews", font=self.manage_font.large_bold_heading_font).pack(anchor=tk.W, pady=(20, 5))
        tk.Label(content, text="Read what our members say about their FitZone experience.",
                 font=self.manage_font.medium_letters_font).pack(anchor=tk.W, pady=(0, 20))

        self.reviews_frame = tk.Frame(content)
        self.reviews_frame.pack(fill=tk.X)

        self.load_reviews()

        if self.member_id:
            separator = ttk.Separator(content, orient="horizontal")
            separator.pack(fill=tk.X, pady=20)

            tk.Label(content, text="Leave a Review", font=self.manage_font.medium_bold_heading_font).pack(anchor=tk.W)

            self.create_review_form(content)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def load_reviews(self):
        for widget in self.reviews_frame.winfo_children():
            widget.destroy()

        try:
            self.cursor.execute(
                """
                SELECT m.FirstName || ' ' || m.LastName, r.Rating, r.ReviewText, r.ReviewDate
                FROM Reviews r
                JOIN Members m ON r.MemberID = m.MemberID
                WHERE r.LocationID = ?
                ORDER BY r.ReviewDate DESC
                """,
                (self.location_id,)
            )
            reviews = self.cursor.fetchall()

            if not reviews:
                tk.Label(
                    self.reviews_frame,
                    text="No reviews yet. Be the first to leave a review!",
                    font=self.manage_font.medium_letters_font
                ).pack(pady=20)
                return

            avg_rating = sum(r[1] for r in reviews) / len(reviews)
            tk.Label(
                self.reviews_frame,
                text=f"Average Rating: {'★' * round(avg_rating)}{'☆' * (5 - round(avg_rating))} ({avg_rating:.1f}/5) - {len(reviews)} review(s)",
                font=self.manage_font.medium_bold_letters_font
            ).pack(anchor=tk.W, pady=5)

            for name, rating, review_text, review_date in reviews:
                card = tk.Frame(self.reviews_frame, background="#FFFFFF", relief=tk.GROOVE, bd=1)
                card.pack(fill=tk.X, pady=8)

                header = tk.Frame(card, background="#F9F9F9")
                header.pack(fill=tk.X, padx=10, pady=5)

                tk.Label(header, text=name, font=self.manage_font.medium_bold_letters_font, background="#F9F9F9").pack(side=tk.LEFT)
                stars = "★" * rating + "☆" * (5 - rating)
                tk.Label(header, text=stars, font=self.manage_font.medium_letters_font,
                         background="#F9F9F9", foreground="#FFD700").pack(side=tk.LEFT, padx=10)
                tk.Label(header, text=str(review_date), font=self.manage_font.smaller_letters_font,
                         background="#F9F9F9", foreground="#888888").pack(side=tk.RIGHT)

                if review_text:
                    tk.Label(card, text=review_text, font=self.manage_font.medium_letters_font,
                             background="#FFFFFF", wraplength=900).pack(anchor=tk.W, padx=15, pady=5)

        except sqlite3.Error as e:
            self.message_handler.invalid_message(f"Error loading reviews: {e}")

    def create_review_form(self, parent):
        form_frame = tk.Frame(parent)
        form_frame.pack(fill=tk.X, pady=10)

        tk.Label(form_frame, text="Rating:", font=self.manage_font.medium_bold_letters_font).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.rating_var = tk.IntVar(value=5)
        ratings_frame = tk.Frame(form_frame)
        ratings_frame.grid(row=0, column=1, padx=5, sticky=tk.W)
        for i in range(1, 6):
            tk.Radiobutton(
                ratings_frame, text=f"{'★' * i}",
                variable=self.rating_var, value=i,
                font=self.manage_font.medium_letters_font, foreground="#FFD700"
            ).pack(side=tk.LEFT)

        tk.Label(form_frame, text="Review:", font=self.manage_font.medium_bold_letters_font).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.review_text = tk.Text(form_frame, width=80, height=5, font=self.manage_font.medium_letters_font)
        self.review_text.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(
            form_frame, text="Submit Review",
            font=self.manage_font.medium_bold_letters_font,
            background="#4CAF50", foreground="#FFFFFF",
            command=self.submit_review
        ).grid(row=2, column=1, sticky=tk.E, padx=5, pady=10)

    def submit_review(self):
        review_text = self.review_text.get("1.0", tk.END).strip()
        rating = self.rating_var.get()

        if not review_text:
            self.message_handler.invalid_message("Error: \n\n \u26A0 Please write a review before submitting.")
            return

        try:
            review_date = datetime.date.today()
            self.cursor.execute(
                "INSERT INTO Reviews (MemberID, LocationID, Rating, ReviewText, ReviewDate) VALUES (?, ?, ?, ?, ?)",
                (self.member_id, self.location_id, rating, review_text, review_date)
            )
            self.conn.commit()
            self.review_text.delete("1.0", tk.END)
            self.message_handler.success_message("Success: \n\n \u2705 Review submitted successfully!")
            self.load_reviews()
        except sqlite3.Error as e:
            self.message_handler.invalid_message(f"Error: \n\n \u26A0 Could not submit review: {e}")
