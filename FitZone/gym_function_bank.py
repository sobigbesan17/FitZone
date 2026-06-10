import tkinter as tk
from tkinter import ttk
from gym_font import ManageFont
from tkcalendar import Calendar
import datetime
import bcrypt
import sqlite3


class MessageHandler:
    def __init__(self, root):
        self.root = root
        self.manage_font = ManageFont()
        self.message_frame = None

    def display_message(self, text, background_color):
        self.message_frame = tk.Frame(self.root, background=background_color)
        self.message_frame.place(relx=0.5, rely=0.14, anchor=tk.CENTER, width=940)

        close_button = tk.Button(
            self.message_frame,
            text="\u2716",
            background=background_color,
            foreground="#FFFFFF",
            command=lambda frame=self.message_frame: self.message_frame.destroy(),
        )
        close_button.pack(anchor="ne")

        message_label = tk.Label(
            self.message_frame,
            text=text,
            background=background_color,
            foreground="#FFFFFF",
            font=self.manage_font.medium_letters_font,
        )
        message_label.pack(padx=10, pady=5)

    def invalid_message(self, error_string):
        self.destroy_messages()
        self.display_message(error_string, "#D11A17")

    def success_message(self, success_string):
        self.destroy_messages()
        self.display_message(success_string, "#4CAF50")

    def info_message(self, info_string):
        self.destroy_messages()
        self.display_message(info_string, "#0074D9")

    def destroy_messages(self):
        if self.message_frame:
            try:
                self.message_frame.destroy()
            except Exception:
                pass
        self.message_frame = None


class ReadText:
    def __init__(self, file_path):
        self.file_path = file_path

    def extract_description(self, title):
        try:
            with open(self.file_path, "r", encoding="utf-8", errors="replace") as file:
                content = file.read()

            content = content.replace("â€¢", "•")

            separator = "---"
            sections = [section.strip() for section in content.split(separator) if section.strip()]

            for index in range(0, len(sections) - 1, 2):
                section_title = sections[index].strip()
                section_body = sections[index + 1].strip()
                if section_title == title:
                    return section_body

            return "Text not found"
        except Exception:
            return "Text not found"


class ValidateCredentials:
    def __init__(self):
        self.conn = sqlite3.connect("FitZone.db")
        self.cursor = self.conn.cursor()

        self.min_password_length = 8
        self.max_password_length = 20

        self.symbols = "!@#$%^&*()_+{}:;<>,.?~"

    def validate_username(self, username):
        if len(username) < 4 or len(username) > 50:
            return "Username must be between 4 and 50 characters."

        if not all(c.isalnum() or c == "_" for c in username):
            return "Username can only contain alphanumeric characters and underscores."

        self.cursor.execute(
            "SELECT Username FROM Members WHERE LOWER(Username) = LOWER(?)",
            (username,),
        )
        existing_username = self.cursor.fetchone()
        if existing_username:
            return "Username already exists. Please choose a different one."

        return None

    def validate_password(self, password, confirm_password_condition, confirm_password=None):
        if len(password) < self.min_password_length:
            return "Password must be at least 8 characters long."

        if len(password) > self.max_password_length:
            return "Password is too long (maximum 20 characters)."

        if confirm_password_condition == 1:
            if password != confirm_password:
                return "Passwords do not match."

        has_lowercase = any(char.islower() for char in password)
        has_uppercase = any(char.isupper() for char in password)
        has_symbol = any(char in self.symbols for char in password)

        if not has_lowercase:
            return "Password must contain at least one lowercase letter."

        if not has_uppercase:
            return "Password must contain at least one uppercase letter."

        if not has_symbol:
            return "Password must contain at least one special symbol (!@#$%^&*()_+{}:;<>,.?~)."

        return []

    def validate_email(self, email):
        if not email:
            return "Error: \n\n \u26A0 Email address is empty."
        elif len(email) > 320:
            return "Error: \n\n \u26A0 Email address is too long."
        else:
            parts = email.split("@")
            if len(parts) != 2:
                return "Error: \n\n \u26A0 Email should contain a single '@' symbol."
            else:
                local_part, domain_part = parts

                if not local_part or not domain_part:
                    return "Error: \n\n \u26A0 Local and domain parts cannot be empty."
                elif len(local_part) > 64:
                    return "Error: \n\n \u26A0 Local part of the email is too long."
                elif len(domain_part) > 255:
                    return "Error: \n\n \u26A0 Domain part of the email is too long."
                elif not domain_part.count(".") >= 1:
                    return "Error: \n\n \u26A0 Email domain should contain at least one '.' symbol."
                elif not all(char.isalnum() or char in "!#$%&'*+-/=?^_`{|}~" for char in local_part):
                    return "Error: \n\n \u26A0 Invalid characters in the local part of the email."
                elif not all(char.isalnum() or char in ".-" for char in domain_part):
                    return "Error: \n\n \u26A0 Invalid characters in the domain part of the email."
                elif domain_part[0] == "." or domain_part[-1] == ".":
                    return "Error: \n\n \u26A0 Domain cannot start or end with a '.'."
                elif ".." in domain_part:
                    return "Error: \n\n \u26A0 Domain cannot contain consecutive '.' characters."
                elif "." not in domain_part:
                    return "Error: \n\n \u26A0 Domain should contain at least one '.' symbol."
                elif email.count("@") > 1:
                    return "Error: \n\n \u26A0 More than one '@' symbol found in the email."

                return None

    def validate_date_of_birth(self, date_of_birth_str):
        try:
            date_of_birth = datetime.datetime.strptime(date_of_birth_str, "%Y-%m-%d").date()

            current_date = datetime.datetime.today().date()
            age = (
                current_date.year
                - date_of_birth.year
                - ((current_date.month, current_date.day) < (date_of_birth.month, date_of_birth.day))
            )

            if date_of_birth > current_date:
                return "Date of birth cannot be in the future."

            if age < 16:
                return "You must be 16 or older to create a gym website account."
            elif age > 100:
                return "Invalid date of birth. Please provide a valid date."

            return None
        except ValueError:
            return "Invalid date format. Please use yyyy-MM-dd."

    def validate_phone_number(self, phone_number):
        if len(phone_number) < 8:
            return "Phone number must be at least 8 digits long."
        elif len(phone_number) > 10:
            return "Phone number is too long (maximum 10 digits)."

        return None


class PasswordHandler:
    def hash_and_store_password(self, password):
        salt = bcrypt.gensalt()
        password = password.encode("utf-8")
        password_hash = bcrypt.hashpw(password, salt)
        return password_hash, salt

    def hash_password(self, provided_password, stored_salt):
        password = provided_password.encode("utf-8")
        password_hash = bcrypt.hashpw(password, stored_salt)
        return password_hash


class TimeFormatHandler:
    def calculate_end_time(self, start_time, duration):
        start_time_obj = datetime.datetime.strptime(start_time, "%H:%M")
        hours, minutes = map(int, duration.split(":"))
        end_time_obj = start_time_obj + datetime.timedelta(hours=hours, minutes=minutes)
        end_time = end_time_obj.strftime("%I:%M %p")
        return end_time

    def convert_to_am_pm(self, start_time):
        start_time_obj = datetime.datetime.strptime(start_time, "%H:%M")
        am_pm_time = start_time_obj.strftime("%I:%M %p")
        return am_pm_time


class CalendarWindow(tk.Toplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.title(title)
        self.manage_font = ManageFont()
        self.geometry("400x400")

        self.calendar = Calendar(self, font=self.manage_font.medium_letters_font)
        self.calendar.pack(padx=10, pady=10, fill="both", expand=True)

        self.select_date_button = tk.Button(
            self,
            text="Select Date",
            font=self.manage_font.medium_letters_font,
            background="#333333",
            foreground="#FFFFFF",
            command=self.set_selected_date,
        )
        self.select_date_button.pack(pady=10)

    def set_selected_date(self):
        selected_date = self.calendar.get_date()
        selected_date = datetime.datetime.strptime(selected_date, "%m/%d/%y")
        formatted_date = selected_date.strftime("%Y-%m-%d")
        self.master.update_start_date(formatted_date)
        self.destroy()


class HorizontalProgressBar:
    def __init__(self, master, progress_value):
        self.master = master
        self.manage_font = ManageFont()
        self.frame = tk.Frame(self.master, background="#D3D3D3")
        self.frame.pack(pady=20, fill="x")
        self.progress_value = progress_value

        ttk.Label(
            self.frame,
            text="Registration Progress:",
            font=self.manage_font.medium_bold_heading_font,
            background="#D3D3D3",
        ).pack(fill="x", padx=10)

        self.create_progress_bar()

    def create_progress_bar(self):
        custom_style = ttk.Style(self.frame)
        try:
            custom_style.theme_use("vista")
        except Exception:
            try:
                custom_style.theme_use("clam")
            except Exception:
                pass
        custom_style.configure(
            "red.Horizontal.TProgressbar", foreground="red", background="red"
        )
        self.progress_bar = ttk.Progressbar(
            self.frame,
            style="red.Horizontal.TProgressbar",
            orient="horizontal",
            length=600,
            mode="determinate",
        )

        self.set_progress(self.progress_value)
        self.progress_bar.pack(padx=10, pady=10, fill="x")

    def set_progress(self, value):
        self.progress_bar["value"] = value
