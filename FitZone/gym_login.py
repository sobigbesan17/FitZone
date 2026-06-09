import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
import bcrypt
from gym_font import ManageFont
from gym_function_bank import MessageHandler, PasswordHandler


class GymLogin(GymBasePage):
    def __init__(self, select_your_gym_callback, forgot_password_callback,
                 successful_login_callback, message_error=None):
        super().__init__()
        self.title("FitZone - Login")
        self.successful_login_callback = successful_login_callback

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)
        self.password_handler = PasswordHandler()

        self.conn = sqlite3.connect("FitZone.db")
        self.cursor = self.conn.cursor()

        self.password_field = 0
        self.username_field = 0
        self.member_id = None
        self.location_id = None

        style = ttk.Style(self)
        style.configure("TFrame", background="#333333", foreground="#FFFFFF")

        self.configure(background="#f2f2f2")

        login_frame = tk.Frame(self, background="#333333")
        login_frame.place(relx=0.5, rely=0.37, anchor=tk.CENTER)

        sign_up_description = tk.Label(
            login_frame,
            text="Log Into Your Account",
            background="#333333",
            foreground="#FFFFFF",
            font=self.manage_font.large_bold_heading_font,
        )
        sign_up_description.grid(row=0, column=0, padx=10, pady=5, columnspan=3, sticky="w")

        sign_up_label = tk.Label(
            login_frame,
            text="Do not have an account?",
            background="#333333",
            foreground="#FFFFFF",
            font=self.manage_font.medium_letters_font,
        )
        sign_up_label.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 5), sticky="w")

        sign_up_here_label = tk.Label(
            login_frame,
            text="Sign up here",
            background="#333333",
            foreground="#FFD700",
            font=self.manage_font.medium_underline_letters_font,
            cursor="hand2",
        )
        sign_up_here_label.grid(row=1, column=1, padx=90, pady=(0, 5), sticky="w")
        sign_up_here_label.bind("<Button-1>", lambda event: select_your_gym_callback())

        label_username = tk.Label(
            login_frame,
            text="Username:",
            background="#333333",
            foreground="#FFFFFF",
            font=self.manage_font.medium_letters_font,
        )
        label_username.grid(row=2, column=0, padx=10, pady=5, sticky="e")

        self.entry_username = ttk.Entry(
            login_frame, name="username_entry", width=74,
            font=self.manage_font.medium_letters_font,
        )
        self.entry_username.grid(row=2, column=1, padx=10, pady=5)
        self.entry_username.insert(0, "Enter your username")
        self.entry_username.bind("<FocusIn>", self.on_entry_click)
        self.entry_username.config(foreground="#888888")

        label_password = tk.Label(
            login_frame,
            text="Password:",
            background="#333333",
            foreground="#FFFFFF",
            font=self.manage_font.medium_letters_font,
        )
        label_password.grid(row=3, column=0, padx=10, pady=5, sticky="e")

        self.entry_password = ttk.Entry(
            login_frame, name="password_entry", width=74, show="*",
            font=self.manage_font.medium_letters_font,
        )
        self.entry_password.grid(row=3, column=1, padx=10, pady=5)
        self.entry_password.insert(0, "Enter your password")
        self.entry_password.bind("<FocusIn>", self.on_entry_click)
        self.entry_password.config(foreground="#888888")

        show_password_var = tk.BooleanVar(value=False)
        show_password_checkbox = tk.Checkbutton(
            login_frame,
            text="Show Password",
            background="#333333",
            foreground="#FFFFFF",
            selectcolor="#555555",
            font=self.manage_font.medium_letters_font,
            variable=show_password_var,
            command=lambda: self.toggle_password(show_password_var),
        )
        show_password_checkbox.grid(row=3, column=2, padx=10, pady=5)

        self.login_button = tk.Button(
            login_frame,
            text="Login",
            command=self.validate_login_inputs,
            width=15,
            background="#FFE4B5",
            foreground="#000000",
            font=self.manage_font.small_bold_heading_font,
        )
        self.login_button.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        forgot_password_label = tk.Label(
            login_frame,
            text="Forgot Password?",
            background="#333333",
            foreground="#FFD700",
            font=self.manage_font.medium_underline_letters_font,
            cursor="hand2",
        )
        forgot_password_label.grid(row=5, column=0, columnspan=3, padx=10, pady=5)
        forgot_password_label.bind("<Button-1>", lambda event: forgot_password_callback())

        if message_error:
            self.message_handler.invalid_message(message_error)

    def on_entry_click(self, event):
        entry = event.widget
        if entry.get() == "Enter your username":
            self.username_field = 1
            entry.delete(0, "end")
            entry.insert(0, "")
            entry.config(foreground="black")
        elif entry.get() == "Enter your password":
            self.password_field = 1
            entry.delete(0, "end")
            entry.insert(0, "")
            entry.config(show="*", foreground="black")

    def toggle_password(self, show_var):
        if show_var.get():
            self.entry_password.config(show="")
        else:
            self.entry_password.config(show="*")

    def validate_login_inputs(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        if self.username_field == 0 or not username or username == "Enter your username":
            self.message_handler.invalid_message("Error: \n\n \u26A0 Please enter your username.")
            return

        if self.password_field == 0 or not password or password == "Enter your password":
            self.message_handler.invalid_message("Error: \n\n \u26A0 Please enter your password.")
            return

        self.validate_credentials(username, password)

    def validate_credentials(self, username, password):
        try:
            self.cursor.execute(
                "SELECT MemberID, Password, Salt, LocationID FROM Members WHERE Username = ?",
                (username,),
            )
            result = self.cursor.fetchone()

            if result:
                member_id, stored_hash, stored_salt, location_id = result
                if isinstance(stored_salt, str):
                    stored_salt = stored_salt.encode("utf-8")
                if isinstance(stored_hash, str):
                    stored_hash = stored_hash.encode("utf-8")

                computed_hash = self.password_handler.hash_password(password, stored_salt)
                if computed_hash == stored_hash:
                    self.member_id = member_id
                    self.location_id = location_id
                    self.username = username
                    success_string = "Success: \n\n \u2705 Login successful! Redirecting..."
                    self.message_handler.success_message(success_string)
                    self.after(500, self.perform_success)
                else:
                    self.message_handler.invalid_message(
                        "Error: \n\n \u26A0 Invalid username or password."
                    )
            else:
                self.message_handler.invalid_message(
                    "Error: \n\n \u26A0 Invalid username or password."
                )
        except sqlite3.Error as e:
            self.message_handler.invalid_message(f"Error: \n\n \u26A0 Database error: {e}")

    def perform_success(self):
        self.successful_login_callback()

    def get_member_id(self):
        return self.member_id

    def get_location_id(self):
        return self.location_id
