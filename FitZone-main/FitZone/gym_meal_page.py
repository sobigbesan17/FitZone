import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
from gym_font import ManageFont
from gym_function_bank import MessageHandler


class GymMealPage(GymBasePage):
    def __init__(self, member_id, location_id, home_callback, dashboard_callback=None):
        super().__init__()
        self.title("FitZone - Meals")
        self.geometry("1100x700")
        self.member_id = member_id
        self.location_id = location_id
        self.home_callback = home_callback
        self.dashboard_callback = dashboard_callback

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)

        self.conn = sqlite3.connect("FitZone.db")
        self.cursor = self.conn.cursor()

        self.configure(background="#f2f2f2")
        self.create_meals_page()

    def create_meals_page(self):
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

        if self.dashboard_callback:
            tk.Button(
                nav_frame, text="My Dashboard",
                font=self.manage_font.medium_letters_font,
                background="#FFE4B5", foreground="#000000",
                command=self.dashboard_callback
            ).pack(side=tk.RIGHT, padx=10, pady=5)

        tk.Label(content, text="Healthy Meals", font=self.manage_font.large_bold_heading_font).pack(anchor=tk.W, pady=(20, 5))
        tk.Label(content, text="Browse our selection of nutritious meals to fuel your fitness journey.",
                 font=self.manage_font.medium_letters_font).pack(anchor=tk.W, pady=(0, 10))

        filter_frame = tk.Frame(content)
        filter_frame.pack(fill=tk.X, pady=10)

        tk.Label(filter_frame, text="Meal Type:", font=self.manage_font.medium_bold_letters_font).grid(row=0, column=0, padx=5)
        self.meal_type_var = tk.StringVar(value="All")
        meal_types = ["All", "Breakfast", "Lunch", "Dinner", "Snack"]
        meal_type_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.meal_type_var,
            values=meal_types,
            state="readonly",
            width=15,
            font=self.manage_font.medium_letters_font,
        )
        meal_type_combo.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Dietary:", font=self.manage_font.medium_bold_letters_font).grid(row=0, column=2, padx=5)
        self.dietary_var = tk.StringVar(value="All")
        dietary_opts = ["All", "Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free"]
        dietary_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.dietary_var,
            values=dietary_opts,
            state="readonly",
            width=15,
            font=self.manage_font.medium_letters_font,
        )
        dietary_combo.grid(row=0, column=3, padx=5)

        tk.Label(filter_frame, text="Sort by:", font=self.manage_font.medium_bold_letters_font).grid(row=0, column=4, padx=5)
        self.sort_var = tk.StringVar(value="Calories (Low to High)")
        sort_opts = ["Calories (Low to High)", "Calories (High to Low)", "Protein (High to Low)", "Cooking Time (Low to High)"]
        sort_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.sort_var,
            values=sort_opts,
            state="readonly",
            width=25,
            font=self.manage_font.medium_letters_font,
        )
        sort_combo.grid(row=0, column=5, padx=5)

        self.meals_content_frame = tk.Frame(content)
        self.meals_content_frame.pack(fill=tk.X)

        tk.Button(
            filter_frame, text="Apply Filter",
            font=self.manage_font.medium_letters_font,
            background="#333333", foreground="#FFFFFF",
            command=self.load_meals
        ).grid(row=0, column=6, padx=10)

        self.load_meals()
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def load_meals(self):
        for widget in self.meals_content_frame.winfo_children():
            widget.destroy()

        try:
            query = "SELECT MealID, MealName, MealType, Calories, Protein, Fat, Carbohydrates, CookingTime, MealSummary, DietaryRestrictions FROM Meals WHERE 1=1"
            params = []

            if self.meal_type_var.get() != "All":
                query += " AND MealType = ?"
                params.append(self.meal_type_var.get())

            if self.dietary_var.get() != "All":
                query += " AND DietaryRestrictions LIKE ?"
                params.append(f"%{self.dietary_var.get()}%")

            sort = self.sort_var.get()
            if sort == "Calories (Low to High)":
                query += " ORDER BY Calories ASC"
            elif sort == "Calories (High to Low)":
                query += " ORDER BY Calories DESC"
            elif sort == "Protein (High to Low)":
                query += " ORDER BY Protein DESC"
            elif sort == "Cooking Time (Low to High)":
                query += " ORDER BY CookingTime ASC"

            self.cursor.execute(query, params)
            meals = self.cursor.fetchall()

            if not meals:
                tk.Label(
                    self.meals_content_frame,
                    text="No meals found matching your criteria.",
                    font=self.manage_font.medium_letters_font
                ).pack(pady=20)
                return

            for i, meal in enumerate(meals):
                meal_id, name, mtype, calories, protein, fat, carbs, cook_time, summary, dietary = meal

                card = tk.Frame(self.meals_content_frame, background="#FFFFFF", relief=tk.GROOVE, bd=1)
                card.pack(fill=tk.X, pady=8)

                header_bg = "#FFF5E6" if i % 2 == 0 else "#F0F8FF"
                header = tk.Frame(card, background=header_bg)
                header.pack(fill=tk.X, padx=10, pady=5)

                tk.Label(header, text=name, font=self.manage_font.larger_bold_letters_font, background=header_bg).pack(side=tk.LEFT)
                tk.Label(header, text=mtype, font=self.manage_font.smaller_letters_font,
                         background="#D11A17", foreground="#FFFFFF", padx=5).pack(side=tk.RIGHT, padx=5)

                info_frame = tk.Frame(card, background="#FFFFFF")
                info_frame.pack(fill=tk.X, padx=10, pady=5)

                stats = f"Calories: {calories} kcal | Protein: {protein}g | Fat: {fat}g | Carbs: {carbs}g | Cook Time: {cook_time} min"
                tk.Label(info_frame, text=stats, font=self.manage_font.smaller_letters_font, background="#FFFFFF").pack(anchor=tk.W)

                if summary:
                    tk.Label(info_frame, text=summary, font=self.manage_font.smaller_letters_font,
                             background="#FFFFFF", foreground="#555555", wraplength=900).pack(anchor=tk.W, pady=3)

                if dietary and dietary != "None":
                    tk.Label(info_frame, text=f"Dietary: {dietary}", font=self.manage_font.smaller_letters_font,
                             background="#FFFFFF", foreground="#4CAF50").pack(anchor=tk.W)

                if self.member_id:
                    tk.Button(
                        card, text="Add to Meal Plan",
                        font=self.manage_font.smaller_letters_font,
                        background="#4CAF50", foreground="#FFFFFF",
                        command=lambda mid=meal_id, mn=name: self.add_to_meal_plan(mid, mn)
                    ).pack(anchor=tk.E, padx=10, pady=5)

        except sqlite3.Error as e:
            self.message_handler.invalid_message(f"Error loading meals: {e}")

    def add_to_meal_plan(self, meal_id, meal_name):
        import datetime
        try:
            plan_date = datetime.date.today()
            self.cursor.execute(
                "INSERT INTO MealPlans (MemberID, MealID, PlanDate, MealTime) VALUES (?, ?, ?, ?)",
                (self.member_id, meal_id, plan_date, "Unspecified")
            )
            self.conn.commit()
            self.message_handler.success_message(f"Success: \n\n \u2705 '{meal_name}' added to your meal plan!")
        except sqlite3.Error as e:
            self.message_handler.invalid_message(f"Error: \n\n \u26A0 Could not add to meal plan: {e}")
