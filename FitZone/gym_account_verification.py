import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
import time
import random
from gym_font import ManageFont
from gym_function_bank import MessageHandler, ReadText
from gym_email_verification import EmailVerification

class GymAccountVerification(GymBasePage):
    def __init__(self, email, username, set_new_password_callback):
        super().__init__()
        self.title("FitZone - Account Verification")
        self.set_new_password_callback = set_new_password_callback

        self.email = email
        self.username = username
        self.member_id = None
        self.verification_code = None
        self.verification_code_sent_time = None

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)
        self.configure(background="#f2f2f2")

        style = ttk.Style(self)
        style.configure("TFrame", background="#333333", foreground="#FFFFFF")

        verification_frame = tk.Frame(self, background="#333333")
        verification_frame.place(relx=0.5, rely=0.35, anchor=tk.CENTER)

        title_label = tk.Label(
            verification_frame,
            text="Account Verification",
            background="#333333",
            foreground="#FFFFFF",
            font=self.manage_font.large_bold_heading_font,
        )
        title_label.grid(row=0, column=0, padx=10, pady=5, columnspan=7, sticky="w")

        desc_label = tk.Label(
            verification_frame,
            text="Enter the 6-digit verification code sent to your email address.",
            background="#333333",
            foreground="#AAAAAA",
            font=self.manage_font.medium_letters_font,
        )
        desc_label.grid(row=1, column=0, padx=10, pady=(0, 10), columnspan=7, sticky="w")

        self.code_entries = []
        self.code_fields = [0] * 6
        self.email_verifier = EmailVerification()

        for i in range(6):
            entry = ttk.Entry(
                verification_frame,
                name=f"code_entry{i}",
                width=5,
                font=self.manage_font.large_bold_heading_font,
                justify="center",
            )
            entry.grid(row=2, column=i, padx=5, pady=10)
            entry.insert(0, "0")
            entry.bind("<FocusIn>", self.on_entry_click)
            entry.config(foreground="#888888")
            self.code_entries.append(entry)

        self.verify_button = tk.Button(
            verification_frame,
            text="Verify Code",
            command=self.verify_code,
            width=15,
            background="#FFE4B5",
            foreground="#000000",
            font=self.manage_font.small_bold_heading_font,
        )
        self.verify_button.grid(row=3, column=0, columnspan=7, padx=10, pady=10, sticky="ew")

        self.resend_label = tk.Label(
            verification_frame,
            text="Resend Code",
            background="#333333",
            foreground="#FFD700",
            font=self.manage_font.medium_underline_letters_font,
            cursor="hand2",
        )
        self.resend_label.grid(row=4, column=0, columnspan=7, padx=10, pady=5)
        self.resend_label.bind("<Button-1>", lambda e: self.send_code())

        self.continue_button = tk.Button(
            verification_frame,
            text="Continue",
            command=self.proceed_to_set_password,
            width=15,
            background="#4CAF50",
            foreground="#FFFFFF",
            font=self.manage_font.small_bold_heading_font,
            state=tk.DISABLED,
        )
        self.continue_button.grid(row=5, column=0, columnspan=7, padx=10, pady=10, sticky="ew")

        self.send_code()

    def generate_verification_code(self):
        return str(random.randint(100000, 999999))

    def send_code(self):
        self.verification_code = self.email_verifier.verify_email(
            self.email,
            "FitZone Password Reset",
            "Your FitZone verification code has been requested.",
        )

        info = self.email_verifier.get_info_string()
        if self.email_verifier.is_sent():
            self.verification_code_sent_time = time.time()
            self.message_handler.info_message(info)
        else:
            self.verification_code = None
            self.verification_code_sent_time = None
            self.message_handler.invalid_message(info)

    def verify_code(self):
        self.error_string = ""
        self.success_string = ""

        code = "".join(entry.get() for entry in self.code_entries)
        correct_code_format = len(code) == 6 and code.isdigit()

        if correct_code_format and code == self.verification_code:
            if self.verification_code_sent_time is not None:
                current_time = time.time()
                time_difference = current_time - self.verification_code_sent_time
                if time_difference > 600:
                    self.error_string = "Error: \n\n \u26A0 Verification code has expired. Please request a new code. \n"
                else:
                    self.success_string = "Success: \n\n \u2705 Code verification successful! \n"
                    self._check_member()
        elif not correct_code_format:
            self.error_string = "Error: \n\n \u26A0 Please enter the six-digit verification code. \n"
        else:
            self.error_string = "Error: \n\n \u26A0 Invalid code. Please try again. \n"

        if self.error_string:
            self.message_handler.invalid_message(self.error_string)

        if self.success_string:
            self.message_handler.success_message(self.success_string)
            self.display_continue_button()
            self.disable_inputs_after_verification()

    def _check_member(self):
        try:
            conn = sqlite3.connect("FitZone.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT MemberID FROM Members WHERE Email = ? AND Username = ?",
                (self.email, self.username),
            )
            record = cursor.fetchone()
            conn.close()
            if record:
                self.member_id = record[0]
        except sqlite3.Error as e:
            print("Error occurred:", e)

    def on_entry_click(self, event):
        entry = event.widget
        try:
            name = entry.winfo_name()
            index = int(name[-1])
            self.code_fields[index] = 1
        except (ValueError, IndexError):
            pass
        entry.delete(0, "end")
        entry.config(foreground="black")

    def disable_inputs_after_verification(self):
        self.verify_button.config(state=tk.DISABLED)
        self.resend_label.unbind("<Button-1>")
        self.resend_label.config(cursor="arrow")
        for entry in self.code_entries:
            entry.config(state=tk.DISABLED)

    def display_continue_button(self):
        self.continue_button.config(state=tk.NORMAL)

    def proceed_to_set_password(self):
        self.set_new_password_callback()

    def get_member_id(self):
        return self.member_id
