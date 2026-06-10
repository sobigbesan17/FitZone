import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
from gym_font import ManageFont
from gym_function_bank import MessageHandler, ValidateCredentials


class GymForgotPassword(GymBasePage):
    def __init__(self, account_verification_callback):
        super().__init__()
        self.title("FitZone - Forgot Password")
        self.account_verification_callback = account_verification_callback

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)
        self.validate_credentials = ValidateCredentials()

        self.username_field = 0
        self.email_field = 0
        self.email = ""
        self.username = ""

        self.configure(background="#f2f2f2")

        style = ttk.Style(self)
        style.configure("TFrame", background="#333333", foreground="#FFFFFF")

        forgot_password_frame = tk.Frame(self, background="#333333")
        forgot_password_frame.place(relx=0.5, rely=0.33, anchor=tk.CENTER)

        description_label = tk.Label(
            forgot_password_frame,
            text="Forgot Password",
            background="#333333",
            foreground="#FFFFFF",
            font=self.manage_font.large_bold_heading_font,
        )
        description_label.grid(row=0, column=0, padx=10, pady=5, columnspan=2, sticky="w")

        desc_info = tk.Label(
            forgot_password_frame,
            text="Enter your username and registered email address to reset your password.",
            background="#333333",
            foreground="#AAAAAA",
            font=self.manage_font.medium_letters_font,
        )
        desc_info.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")

        username_label = tk.Label(
            forgot_password_frame,
            text="Username:",
            background="#333333",
            foreground="#FFFFFF",
            font=self.manage_font.medium_letters_font,
        )
        username_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")

        self.entry_username = ttk.Entry(
            forgot_password_frame, name="username_entry", width=74,
            font=self.manage_font.medium_letters_font,
        )
        self.entry_username.grid(row=2, column=1, padx=10, pady=5)
        self.entry_username.insert(0, "Enter your username")
        self.entry_username.bind("<FocusIn>", self.on_entry_click)
        self.entry_username.config(foreground="#888888")

        label_email = tk.Label(
            forgot_password_frame,
            text="Email:",
            background="#333333",
            foreground="#FFFFFF",
            font=self.manage_font.medium_letters_font,
        )
        label_email.grid(row=3, column=0, padx=10, pady=5, sticky="e")

        self.entry_email = ttk.Entry(
            forgot_password_frame, name="email_entry", width=74,
            font=self.manage_font.medium_letters_font,
        )
        self.entry_email.grid(row=3, column=1, padx=10, pady=5)
        self.entry_email.insert(0, "Enter your email")
        self.entry_email.bind("<FocusIn>", self.on_entry_click)
        self.entry_email.config(foreground="#888888")

        self.reset_button = tk.Button(
            forgot_password_frame,
            text="Reset Password",
            command=self.validate_reset_password,
            width=15,
            background="#FFE4B5",
            foreground="#000000",
            font=self.manage_font.small_bold_heading_font,
        )
        self.reset_button.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

    def validate_reset_password(self):
        self.error_string = ""
        self.email = ""
        self.username = ""

        self.username = self.entry_username.get()
        self.email = self.entry_email.get()
        self.error_string = self.validate_credentials.validate_email(self.email)

        if (self.username and not self.error_string) and self.username_field == 1 and self.email_field == 1:
            self.reset_button.bind("<Button-1>", lambda event, func=self.account_verification_callback: func())
            self.reset_button.event_generate("<Button-1>")
        else:
            if (not (self.email_field == 1 and self.email) and not (self.username_field == 1 and self.username)):
                self.error_string = "Error: \n\n \u26A0 Please enter username and email."
                self.message_handler.invalid_message(self.error_string)
            elif self.email_field == 0 or not self.email:
                self.error_string = "Error: \n\n \u26A0 Please enter email."
                self.message_handler.invalid_message(self.error_string)
            elif self.username_field == 0 or not self.username:
                self.error_string = "Error: \n\n \u26A0 Please enter username."
                self.message_handler.invalid_message(self.error_string)
            else:
                self.message_handler.invalid_message(self.error_string)

    def on_entry_click(self, event):
        entry = event.widget
        if entry.get() == "Enter your username":
            self.username_field = 1
            entry.delete(0, "end")
            entry.insert(0, "")
            entry.config(foreground="black")
        elif entry.get() == "Enter your email":
            self.email_field = 1
            entry.delete(0, "end")
            entry.insert(0, "")
            entry.config(foreground="black")

    def get_email(self):
        return self.email

    def get_username(self):
        return self.username
