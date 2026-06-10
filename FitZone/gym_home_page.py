import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
from pathlib import Path
from PIL import Image, ImageTk
from gym_font import ManageFont
from gym_function_bank import ReadText


class GymHomePage(GymBasePage):
    def __init__(self, login_callback, select_gym_callback, logout_callback,
                 view_gym_team_callback, gym_features_callback,
                 reviews_callback, meal_callback, workout_callback,
                 home_callback, member_id=None, username=None, location_id=None,
                 view_class_schedule_callback=None, gym_class_clashes_callback=None):
        super().__init__()
        self.title("FitZone - Home")
        self.geometry("1200x800")
        self.configure(background="#f2f2f2")

        self.member_id = member_id
        self.username = username
        self.location_id = location_id
        self.login_callback = login_callback
        self.select_gym_callback = select_gym_callback
        self.logout_callback = logout_callback
        self.view_gym_team_callback = view_gym_team_callback
        self.gym_features_callback = gym_features_callback
        self.reviews_callback = reviews_callback
        self.meal_callback = meal_callback
        self.workout_callback = workout_callback
        self.home_callback = home_callback
        self.view_class_schedule_callback = view_class_schedule_callback
        self.gym_class_clashes_callback = gym_class_clashes_callback
        self.update_profile_callback = lambda: None

        self.manage_font = ManageFont()
        self.asset_dir = Path(__file__).resolve().parent
        self._load_images()
        self._create_ui()

    def _load_image(self, filename, size=None):
        path = self.asset_dir / filename
        if not path.exists():
            return None
        try:
            img = Image.open(path)
            if size:
                img = img.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def _load_images(self):
        self.images = {}

        self.images["header_logo"] = self._load_image("Fitzone_Logo.png", (70, 70))
        self.images["hero"] = self._load_image("Placeholder.png", (int(360 * 1.2), 360))
        self.images["feature_strength"] = self._load_image("Placeholder.png", (120, 120))
        self.images["feature_nutrition"] = self._load_image("Placeholder.png", (120, 120))
        self.images["feature_community"] = self._load_image("Placeholder.png", (120, 120))
        self.images["avatar_1"] = self._load_image("Avatar.png", (160, 160))
        self.images["avatar_2"] = self._load_image("Avatar.png", (160, 160))
        self.images["avatar_3"] = self._load_image("Avatar.png", (160, 160))

        self.images["avatars"] = [
            self.images.get("avatar_1"),
            self.images.get("avatar_2"),
            self.images.get("avatar_3"),
        ]

    def _create_ui(self):
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self._create_hero(scrollable_frame)
        self._create_features_section(scrollable_frame)
        self._create_cta_buttons(scrollable_frame)
        self._create_testimonials(scrollable_frame)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

    def _create_nav(self):
        nav = tk.Frame(self, background="#333333", height=60)
        nav.pack(fill=tk.X)
        nav.pack_propagate(False)
        nav.grid_columnconfigure(0, weight=0)
        nav.grid_columnconfigure(1, weight=1)
        nav.grid_columnconfigure(2, weight=0)

        self.menu_button = tk.Button(
            nav,
            text="☰",
            background="#333333",
            foreground="#FFFFFF",
            font=self.manage_font.large_bold_letters_font,
            bd=0,
            activebackground="#444444",
            activeforeground="#FFFFFF",
            cursor="hand2",
            command=self._toggle_nav_menu,
        )
        self.menu_button.grid(row=0, column=0, sticky="w", padx=20, pady=10)

        if self.images.get("header_logo"):
            logo = tk.Label(nav, image=self.images["header_logo"], background="#333333", cursor="hand2")
        else:
            logo = tk.Label(
                nav, text="FitZone", background="#333333", foreground="#FFD700",
                font=self.manage_font.large_bold_heading_font, cursor="hand2"
            )
        logo.grid(row=0, column=1)
        if self.home_callback:
            logo.bind("<Button-1>", lambda e: self.home_callback())

        auth_frame = tk.Frame(nav, background="#333333")
        auth_frame.grid(row=0, column=2, sticky="e", padx=20)

        self.nav_links = [
            ("Home", self.home_callback),
            ("Meals", self.meal_callback),
            ("Workouts", self.workout_callback),
            ("Our Team", self.view_gym_team_callback),
            ("Features", self.gym_features_callback),
            ("Reviews", self.reviews_callback),
        ]

        if self.member_id:
            tk.Button(
                auth_frame, text="Logout",
                background="#D11A17", foreground="#FFFFFF",
                font=self.manage_font.medium_letters_font,
                command=self.logout_callback
            ).pack(side=tk.LEFT, padx=5)
        else:
            tk.Button(
                auth_frame, text="Login",
                background="#FFE4B5", foreground="#000000",
                font=self.manage_font.medium_letters_font,
                command=self.login_callback
            ).pack(side=tk.LEFT, padx=5)

            tk.Button(
                auth_frame, text="Sign Up",
                background="#D11A17", foreground="#FFFFFF",
                font=self.manage_font.medium_letters_font,
                command=self.select_gym_callback
            ).pack(side=tk.LEFT, padx=5)

        self.nav_menu_frame = None

    def _toggle_nav_menu(self):
        if self.nav_menu_frame and self.nav_menu_frame.winfo_exists():
            self.nav_menu_frame.destroy()
            self.nav_menu_frame = None
            return

        self.nav_menu_frame = tk.Frame(self, background="#444444", bd=1, relief=tk.RIDGE)
        self.nav_menu_frame.pack(fill=tk.X)

        for text, cmd in self.nav_links:
            btn = tk.Button(
                self.nav_menu_frame,
                text=text,
                background="#444444",
                foreground="#FFFFFF",
                font=self.manage_font.medium_letters_font,
                relief=tk.FLAT,
                command=lambda c=cmd: c() if c else None,
                anchor="w",
                padx=20,
                pady=8,
            )
            btn.pack(fill=tk.X)

    def _create_hero(self, parent):
        hero_frame = tk.Frame(parent, background="#1A1A1A", height=420)
        hero_frame.pack(fill=tk.X, pady=(0, 20))
        hero_frame.pack_propagate(False)

        left_frame = tk.Frame(hero_frame, background="#1A1A1A")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = tk.Frame(hero_frame, background="#1A1A1A")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=40, pady=40)

        if self.images.get("hero"):
            tk.Label(
                left_frame,
                image=self.images["hero"],
                background="#1A1A1A"
            ).pack(fill=tk.BOTH, expand=True)
        else:
            tk.Label(
                left_frame,
                background="#2B2B2B"
            ).pack(fill=tk.BOTH, expand=True)

        tk.Label(
            right_frame, text="Ignite Your Potential.",
            font=self.manage_font.header_title_font,
            background="#1A1A1A", foreground="#FFD700"
        ).pack(anchor="center")

        tk.Label(
            right_frame, text="Your Fitness Journey Starts Here.",
            font=self.manage_font.large_bold_letters_font,
            background="#1A1A1A", foreground="#FFFFFF"
        ).pack(anchor="center", pady=(5, 10))

        tk.Label(
            right_frame,
            text="Join FitZone today and transform your life with world-class fitness facilities,"
                 "\nexpert instructors, and a supportive community.",
            font=self.manage_font.medium_letters_font,
            background="#1A1A1A", foreground="#BBBBBB", justify="center", wraplength=420
        ).pack(anchor="center", pady=10)

        btn_frame = tk.Frame(right_frame, background="#1A1A1A")
        btn_frame.pack(anchor="center", pady=20)

        tk.Button(
            btn_frame, text="Join Now",
            font=self.manage_font.medium_bold_letters_font,
            background="#D11A17", foreground="#FFFFFF",
            padx=24, pady=10, command=self.select_gym_callback,
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame, text="Learn More",
            font=self.manage_font.medium_bold_letters_font,
            background="#444444", foreground="#FFFFFF",
            padx=24, pady=10, relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=10)

    def _create_features_section(self, parent):
        features_frame = tk.Frame(parent, background="#FFFFFF")
        features_frame.pack(fill=tk.X, padx=40, pady=30)

        tk.Label(
            features_frame, text="Why Choose FitZone?",
            font=self.manage_font.large_bold_heading_font,
            background="#FFFFFF"
        ).pack(pady=(20, 10))

        features_grid = tk.Frame(features_frame, background="#FFFFFF")
        features_grid.pack(pady=10, anchor="center")
        for col_index in range(3):
            features_grid.grid_columnconfigure(col_index, weight=1)

        features = [
            ("strength", "World-Class Equipment", "Access to state-of-the-art gym equipment for all fitness levels."),
            ("nutrition", "Expert Instructors", "Certified personal trainers and fitness coaches at your service."),
            ("community", "Personalised Plans", "Custom workout and meal plans tailored to your goals."),
            ("strength", "Multiple Locations", "Convenient gym locations near you, open 7 days a week."),
            ("nutrition", "FitZone App", "Track your progress and manage your membership on the go."),
            ("community", "Community", "Join a vibrant community of like-minded fitness enthusiasts."),
        ]

        for i, (key, title, desc) in enumerate(features):
            col = i % 3
            row = i // 3
            card = tk.Frame(features_grid, background="#F9F9F9", relief=tk.RIDGE, bd=0, padx=20, pady=20)
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)

            if self.images.get(f"feature_{key}"):
                tk.Label(card, image=self.images[f"feature_{key}"], background="#F9F9F9").pack(pady=(0, 10))
            else:
                tk.Label(card, text="★", font=("Segoe UI", 28), background="#F9F9F9").pack(pady=(0, 10))

            tk.Label(card, text=title, font=self.manage_font.medium_bold_letters_font, background="#F9F9F9").pack(anchor="center")
            tk.Label(card, text=desc, font=self.manage_font.smaller_letters_font,
                     background="#F9F9F9", wraplength=240, justify="center", pady=5).pack(anchor="center")

    def _create_cta_buttons(self, parent):
        read_text = ReadText("home_page_description.txt")
        description = read_text.extract_description("Call to Action:")

        cta_frame = tk.Frame(parent, background="#D11A17")
        cta_frame.pack(fill=tk.X, pady=0, padx=40)

        inner = tk.Frame(cta_frame, background="#D11A17")
        inner.pack(pady=30, fill=tk.X)

        tk.Label(
            inner, text="Ready to Start Your Fitness Journey?",
            font=self.manage_font.large_bold_heading_font,
            background="#D11A17", foreground="#FFFFFF"
        ).pack(anchor="center")

        if description and description != "Text not found":
            tk.Label(
                inner, text=description,
                font=self.manage_font.medium_letters_font,
                background="#D11A17", foreground="#FFE4B5", justify="center", wraplength=980
            ).pack(anchor="center", pady=10)

        btn_frame = tk.Frame(inner, background="#D11A17")
        btn_frame.pack(anchor="center", pady=15)

        tk.Button(
            btn_frame, text="Get Started Today",
            font=self.manage_font.medium_bold_letters_font,
            background="#FFFFFF", foreground="#D11A17",
            padx=24, pady=10, command=self.select_gym_callback,
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=10)

    def _create_testimonials(self, parent):
        testimonials_frame = tk.Frame(parent, background="#F2F2F2")
        testimonials_frame.pack(fill=tk.X, padx=40, pady=30)

        tk.Label(
            testimonials_frame, text="What Our Members Say",
            font=self.manage_font.large_bold_heading_font,
            background="#F2F2F2"
        ).pack(pady=(20, 10))

        db_testimonials = self._load_testimonials()

        if db_testimonials:
            self._create_db_testimonials(testimonials_frame, db_testimonials)
        else:
            self._create_default_testimonials(testimonials_frame)

    def _load_testimonials(self):
        try:
            conn = sqlite3.connect("FitZone.db")
            cursor = conn.cursor()
            cursor.execute(
                """SELECT m.FirstName || ' ' || m.LastName, t.TestimonialText,
                          t.FrameColor, t.NameColor, t.TestimonialColor
                   FROM Testimonials t
                   JOIN Members m ON t.MemberID = m.MemberID
                   LIMIT 6"""
            )
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception:
            return []

    def _create_db_testimonials(self, parent, testimonials):
        grid = tk.Frame(parent, background="#F2F2F2")
        grid.pack(pady=10)

        for i, (name, text, frame_color, name_color, text_color) in enumerate(testimonials):
            col = i % 3
            row = i // 3
            card = tk.Frame(
                grid,
                background=frame_color or "#FFFFFF",
                relief=tk.GROOVE, bd=1, padx=20, pady=20
            )
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

            tk.Label(
                card, text=f'"{text}"',
                font=self.manage_font.smaller_letters_font,
                background=frame_color or "#FFFFFF",
                foreground=text_color or "#333333",
                wraplength=250,
                justify="center"
            ).pack()

            tk.Label(
                card, text=f"- {name}",
                font=self.manage_font.medium_bold_letters_font,
                background=frame_color or "#FFFFFF",
                foreground=name_color or "#000000"
            ).pack()

    def _create_default_testimonials(self, parent):
        testimonials = [
            ("Sarah J.", "FitZone completely transformed my fitness journey! The trainers are incredible.", "#FFFFFF", "#000000"),
            ("Marcus R.", "The facilities are top-notch and the community is so supportive.", "#F0FFF0", "#006400"),
            ("Emily K.", "The personalised meal and workout plans helped me lose 20kg in 6 months!", "#FFF0F0", "#8B0000"),
        ]

        grid = tk.Frame(parent, background="#F2F2F2")
        grid.pack(pady=10)

        for i, (name, text, bg, fg) in enumerate(testimonials):
            card = tk.Frame(grid, background=bg, relief=tk.GROOVE, bd=1, padx=20, pady=20)
            card.grid(row=0, column=i, padx=15, pady=15, sticky="nsew")
            avatar = self.images.get("avatars")[i] if len(self.images.get("avatars", [])) > i else None
            if avatar:
                tk.Label(card, image=avatar, background=bg).pack(fill="x", pady=(0, 10))
            tk.Label(card, text=f'"{text}"', font=self.manage_font.smaller_letters_font,
                     background=bg, foreground="#333333", wraplength=280, justify="center").pack(pady=(0, 10))
            tk.Label(card, text=f"- {name}", font=self.manage_font.medium_bold_letters_font,
                     background=bg, foreground=fg).pack()
