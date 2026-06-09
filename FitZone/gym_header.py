import os
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from PIL import Image, ImageTk
from gym_font import ManageFont


class GymHeader(tk.Frame):
    def __init__(
        self,
        parent,
        login_callback,
        logout_callback,
        signup_callback=None,
        update_profile_callback=None,
        home_callback=None,
        meals_callback=None,
        workouts_callback=None,
        view_gym_team_callback=None,
        view_class_schedule_callback=None,
        view_bmi_visualisation_callback=None,
        gym_class_clashes_callback=None,
        member_id=None,
        username=None,
        profile_image_path=None,
    ):
        self.header_height = 30
        self.header_width = int(parent.winfo_screenwidth() * 1.2)
        super().__init__(parent, background="#333333", height=self.header_height, width=self.header_width)
        self.pack_propagate(False)
        self.manage_font = ManageFont()
        self.member_id = member_id
        self.username = username
        self.profile_image_path = profile_image_path
        self.logo_image = self._load_image("Fitzone_Logo.png", (2*self.header_height, self.header_height))
        self.avatar_image = self._load_profile_image(profile_image_path, (self.header_height, self.header_height)) or self._load_image("Avatar.png", (self.header_height, self.header_height))

        self.login_callback = login_callback
        self.logout_callback = logout_callback
        self.signup_callback = signup_callback
        self.update_profile_callback = update_profile_callback
        self.home_callback = home_callback
        self.meals_callback = meals_callback
        self.workouts_callback = workouts_callback
        self.view_gym_team_callback = view_gym_team_callback
        self.view_class_schedule_callback = view_class_schedule_callback
        self.view_bmi_visualisation_callback = view_bmi_visualisation_callback
        self.gym_class_clashes_callback = gym_class_clashes_callback

        self._create_header()

    def _load_image(self, filename, size=None):
        try:
            path = Path(__file__).resolve().parent / filename
            if not path.exists():
                return None
            img = Image.open(path)
            if size:
                width, height = size
                if width is None and height is not None:
                    ratio = height / img.height
                    width = int(img.width * ratio)
                elif height is None and width is not None:
                    ratio = width / img.width
                    height = int(img.height * ratio)
                img = img.resize((width, height), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def _load_profile_image(self, image_path, size=None):
        if not image_path:
            return None
        try:
            candidate = Path(image_path)
            if not candidate.is_absolute() or not candidate.exists():
                candidate = Path.cwd() / image_path
            if not candidate.exists():
                candidate = Path(__file__).resolve().parent / image_path
            if not candidate.exists():
                return None
            img = Image.open(candidate)
            if size:
                width, height = size
                if width is None and height is not None:
                    ratio = height / img.height
                    width = int(img.width * ratio)
                elif height is None and width is not None:
                    ratio = width / img.width
                    height = int(img.height * ratio)
                img = img.resize((width, height), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def _load_profile_image(self, image_path, size=None):
        if not image_path:
            return None
        try:
            candidate = Path(image_path)
            if not candidate.is_absolute() or not candidate.exists():
                candidate = Path.cwd() / image_path
            if not candidate.exists():
                candidate = Path(__file__).resolve().parent / image_path
            if not candidate.exists():
                return None
            img = Image.open(candidate)
            if size:
                width, height = size
                if width is None and height is not None:
                    ratio = height / img.height
                    width = int(img.width * ratio)
                elif height is None and width is not None:
                    ratio = width / img.width
                    height = int(img.height * ratio)
                img = img.resize((width, height), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def _toggle_menu(self):
        if hasattr(self, "nav_menu") and self.nav_menu.winfo_exists():
            self.nav_menu.destroy()
            return

        if hasattr(self, "nav_menu") and self.nav_menu.winfo_exists():
            self.nav_menu.destroy()

        self.nav_menu = tk.Toplevel(self)
        self.nav_menu.overrideredirect(True)
        self.nav_menu.attributes("-topmost", True)
        self.nav_menu.configure(background="#444444", bd=1, highlightthickness=0)

        x = self.winfo_rootx() + 10
        y = self.winfo_rooty() + self.header_height
        self.nav_menu.geometry(f"+{x}+{y}")

        self.nav_menu.bind("<FocusOut>", lambda event: self._close_nav_menu())
        self.nav_menu.bind("<Escape>", lambda event: self._close_nav_menu())

        for text, cmd in self.nav_items:
            btn = tk.Button(
                self.nav_menu,
                text=text,
                background="#444444",
                foreground="#FFFFFF",
                font=self.manage_font.small_font,
                relief=tk.FLAT,
                command=lambda c=cmd: self._execute_nav_command(c),
                anchor="w",
                padx=10,
                pady=4,
            )
            btn.pack(fill=tk.X, pady=1)

        self.nav_menu.focus_force()

    def _show_user_menu(self, event):
        # Native pop-up dropdown menu triggered by clicking the username or avatar
        user_menu = tk.Menu(self, tearoff=0, background="#444444", foreground="#FFFFFF", activebackground="#333333")
        user_menu.add_command(label="Edit Profile", command=self.update_profile_callback)
        user_menu.add_command(label="Logout", command=self.logout_callback)
        
        # Display menu at the mouse cursor click position
        user_menu.tk_popup(event.x_root, event.y_root)

    def _execute_nav_command(self, cmd):
        self._close_nav_menu()
        if callable(cmd):
            cmd()

    def _close_nav_menu(self):
        if hasattr(self, "nav_menu") and self.nav_menu.winfo_exists():
            try:
                self.nav_menu.destroy()
            except Exception:
                pass

    def _create_header(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        self.nav_items = [
            ("Home", self.home_callback),
            ("Meals", self.meals_callback),
            ("Workouts", self.workouts_callback),
            ("BMI Visualisation", self.view_bmi_visualisation_callback),
            ("Schedule", self.view_class_schedule_callback),
            ("Clashes", self.gym_class_clashes_callback),
            ("Our Team", self.view_gym_team_callback),
        ]

        menu_button = tk.Button(
            self,
            text="☰",
            background="#333333",
            foreground="#FFFFFF",
            font=self.manage_font.small_font,
            bd=0,
            activebackground="#444444",
            activeforeground="#FFFFFF",
            cursor="hand2",
            command=self._toggle_menu,
            padx=4,
            pady=2,
            width=2,
        )
        menu_button.grid(row=0, column=0, sticky="w", padx=10, pady=4)

        if self.logo_image:
            logo_label = tk.Label(self, image=self.logo_image, background="#333333", cursor="hand2")
        else:
            logo_label = tk.Label(
                self,
                text="FitZone",
                background="#333333",
                foreground="#FFD700",
                font=self.manage_font.large_bold_heading_font,
                cursor="hand2",
            )
        logo_label.grid(row=0, column=1, pady=4)
        if callable(self.home_callback):
            logo_label.bind("<Button-1>", lambda e: self.home_callback())

        auth_frame = tk.Frame(self, background="#333333")
        auth_frame.grid(row=0, column=2, sticky="e", padx=10, pady=4)

        if self.member_id:
            username = getattr(self, "username", None)
            display_name = username if username else "User"

            if self.avatar_image:
                avatar_label = tk.Label(
                    auth_frame,
                    image=self.avatar_image,
                    background="#333333",
                    cursor="hand2"
                )
                avatar_label.pack(side=tk.LEFT, padx=(0, 5), pady=2)
                avatar_label.bind("<Button-1>", self._show_user_menu)

            name_label = tk.Label(
                auth_frame,
                text=display_name,
                background="#333333",
                foreground="#FFFFFF",
                font=self.manage_font.medium_letters_font,
                cursor="hand2"
            )
            name_label.pack(side=tk.LEFT, padx=(0, 4), pady=2)
            name_label.bind("<Button-1>", self._show_user_menu)
            
        else:
            login_btn = tk.Button(
                auth_frame,
                text="Login",
                background="#FFE4B5",
                foreground="#000000",
                font=self.manage_font.small_font,
                command=self.login_callback,
                padx=6,
                pady=2,
                width=6,
            )
            login_btn.pack(side=tk.LEFT, padx=4, pady=2)

            signup_btn = tk.Button(
                auth_frame,
                text="Sign Up",
                background="#D11A17",
                foreground="#FFFFFF",
                font=self.manage_font.small_font,
                command=self.signup_callback or self.login_callback,
                padx=6,
                pady=2,
                width=6,
            )
            signup_btn.pack(side=tk.LEFT, padx=4, pady=2)