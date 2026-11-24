import tkinter as tk


class GymBasePage(tk.Tk):
    use_shared_header = True

    def __init__(self):
        super().__init__()
        self.header = None
        self.footer = None
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.configure(background="#f2f2f2")
        self._make_fullscreen_centered()
        self.after(0, self._make_fullscreen_centered)

    def refresh_header(self):
        if getattr(self, "use_shared_header", True):
            try:
                if self.header and self.header.winfo_exists():
                    self.header.destroy()
            except Exception:
                pass
            try:
                if self.footer and self.footer.winfo_exists():
                    self.footer.destroy()
            except Exception:
                pass
            self._create_shared_header()
            self._create_shared_footer()

    def _create_shared_header(self):
        from gym_header import GymHeader

        self.header = GymHeader(
            self,
            login_callback=self._header_login,
            logout_callback=self._header_logout,
            signup_callback=self._header_signup,
            update_profile_callback=self._header_update_profile,
            home_callback=self._header_home,
            meals_callback=self._header_meals,
            workouts_callback=self._header_workouts,
            meal_planner_callback=self._header_meal_planner,
            workout_planner_callback=self._header_workout_planner,
            fitness_dashboard_callback=getattr(self, "view_fitness_dashboard_callback", None),
            view_gym_team_callback=getattr(self, "view_gym_team_callback", None),
            view_class_schedule_callback=getattr(self, "view_class_schedule_callback", None),
            view_class_reservations_callback=getattr(self, "view_class_reservations_callback", None),
            gym_class_booking_callback=getattr(self, "gym_class_booking_callback", None),
            calculate_bmi_callback=getattr(self, "calculate_bmi_callback", None),
            view_bmi_visualisation_callback=getattr(self, "view_bmi_visualisation_callback", None),
            gym_class_clashes_callback=getattr(self, "gym_class_clashes_callback", None),
            reviews_callback=getattr(self, "reviews_callback", None),
            modify_classes_callback=getattr(self, "modify_classes_callback", None),
            member_id=getattr(self, "member_id", None),
            username=getattr(self, "username", None),
            profile_image_path=getattr(self, "profile_image_path", None),
        )
        first_child = next(
            (child for child in self.winfo_children()
             if child is not self.header and child.winfo_manager() == "pack"),
            None
        )
        if first_child:
            try:
                self.header.pack(side="top", fill="x", before=first_child)
            except tk.TclError:
                self.header.pack(side="top", fill="x")
        else:
            self.header.pack(side="top", fill="x")
        try:
            self.header.lift()
            self.after_idle(self.header.lift)
        except Exception:
            pass

    def _create_shared_footer(self):
        from gym_footer import GymFooter

        try:
            if self.footer and self.footer.winfo_exists():
                self.footer.destroy()
        except Exception:
            pass

        self.footer = GymFooter(self)
        self.footer.pack(side="bottom", fill="x")

    def _header_login(self):
        callback = getattr(self, "login_callback", None)
        if callable(callback):
            callback()

    def _header_logout(self):
        callback = getattr(self, "logout_callback", None)
        if callable(callback):
            callback()

    def _header_update_profile(self):
        callback = getattr(self, "update_profile_callback", None)
        if callable(callback):
            callback()

    def _header_home(self):
        callback = getattr(self, "home_callback", None)
        if callable(callback):
            callback()

    def _header_meals(self):
        callback = getattr(self, "meal_callback", None)
        if callable(callback):
            callback()

    def _header_workouts(self):
        callback = getattr(self, "workout_callback", None)
        if callable(callback):
            callback()

    def _header_signup(self):
        callback = getattr(self, "signup_callback", None)
        if callable(callback):
            callback()

    def _header_meal_planner(self):
        callback = getattr(self, "meal_planner_callback", None)
        if callable(callback):
            callback()

    def _header_workout_planner(self):
        callback = getattr(self, "workout_planner_callback", None)
        if callable(callback):
            callback()

    def _header_reviews(self):
        callback = getattr(self, "reviews_callback", None)
        if callable(callback):
            callback()

    def _header_modify_classes(self):
        callback = getattr(self, "modify_classes_callback", None)
        if callable(callback):
            callback()

    def _header_fitness_dashboard(self):
        callback = getattr(self, "view_fitness_dashboard_callback", None)
        if callable(callback):
            callback()

    def _make_fullscreen_centered(self):
        self.update_idletasks()
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(f"{width}x{height}+0+0")
        self.state("zoomed")
        try:
            self.eval('tk::PlaceWindow %s center' % self.winfo_toplevel())
        except Exception:
            pass
