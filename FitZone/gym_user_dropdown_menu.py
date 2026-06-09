Aimport tkinter as tk
from gym_font import ManageFont


class GymUserDropdownMenu(tk.Frame):
    def __init__(
        self,
        parent,
        dashboard_callback=None,
        calculate_bmi_callback=None,
        bmi_visualisation_callback=None,
        gym_meal_planner_callback=None,
        gym_workout_planner_callback=None,
        view_class_schedule_callback=None,
        gym_class_booking_callback=None,
        gym_class_clashes_callback=None,
    ):
        super().__init__(parent, background="#333333")
        self.manage_font = ManageFont()
        self.dashboard_callback = dashboard_callback
        self.calculate_bmi_callback = calculate_bmi_callback
        self.bmi_visualisation_callback = bmi_visualisation_callback
        self.gym_meal_planner_callback = gym_meal_planner_callback
        self.gym_workout_planner_callback = gym_workout_planner_callback
        self.view_class_schedule_callback = view_class_schedule_callback
        self.gym_class_booking_callback = gym_class_booking_callback
        self.gym_class_clashes_callback = gym_class_clashes_callback
        self.update_profile_callback = getattr(parent, "update_profile_callback", None)
        self.logout_callback = getattr(parent, "logout_callback", None)
        self._create_menu()

    def _create_menu(self):
        user_label = tk.Label(
            self,
            text="\u25BC My Account",
            background="#333333",
            foreground="#FFFFFF",
            font=self.manage_font.medium_letters_font,
            cursor="hand2",
        )
        user_label.pack(side=tk.LEFT, padx=10)
        user_label.bind("<Button-1>", self._toggle_dropdown)

        self.dropdown_frame = None

    def _toggle_dropdown(self, event=None):
        if self.dropdown_frame and self.dropdown_frame.winfo_exists():
            self.dropdown_frame.destroy()
            self.dropdown_frame = None
            return

        self.dropdown_frame = tk.Frame(
            self.master,
            background="#444444",
            relief=tk.RAISED,
            bd=1,
        )
        self.dropdown_frame.place(x=event.x_root, y=event.y_root + 20)

        options = [
            ("Dashboard", self.dashboard_callback),
            ("Update Profile", self.update_profile_callback),
            ("Logout", self.logout_callback),
        ]
        for text, cmd in options:
            btn = tk.Button(
                self.dropdown_frame,
                text=text,
                background="#444444",
                foreground="#FFFFFF",
                font=self.manage_font.medium_letters_font,
                relief=tk.FLAT,
                command=lambda c=cmd: (self.dropdown_frame.destroy(), c()) if c else None,
                anchor="w",
                width=15,
            )
            btn.pack(fill=tk.X, padx=2, pady=1)


class GymPagesDropdownMenu(tk.Frame):
    def __init__(self, parent, location_id, member_id, callbacks=None):
        super().__init__(parent, background="#f2f2f2")
        self.manage_font = ManageFont()
        self.location_id = location_id
        self.member_id = member_id
        self.callbacks = callbacks or {}
        self._create_nav_tabs()

    def _create_nav_tabs(self):
        tabs = [
            ("Dashboard", "dashboard"),
            ("BMI Calculator", "bmi"),
            ("BMI Visualisation", "bmi_vis"),
            ("Meal Planner", "meal_planner"),
            ("Workout Planner", "workout_planner"),
            ("Class Schedule", "class_schedule"),
            ("Book Class", "book_class"),
            ("Class Clashes", "class_clashes"),
        ]

        for text, key in tabs:
            btn = tk.Button(
                self,
                text=text,
                background="#333333",
                foreground="#FFFFFF",
                font=self.manage_font.smaller_letters_font,
                relief=tk.FLAT,
                padx=8,
                pady=4,
                command=lambda k=key: self._handle_click(k),
            )
            btn.pack(side=tk.LEFT, padx=2, pady=5)

    def _handle_click(self, key):
        cb = self.callbacks.get(key)
        if cb:
            cb()
