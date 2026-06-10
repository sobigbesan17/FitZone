import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
from gym_font import ManageFont
from gym_function_bank import MessageHandler


class GymRegistrationSuccessPage(GymBasePage):
    def __init__(self, users_detail, home_callback):
        super().__init__()
        self.title("FitZone - Registration Success")
        self.geometry("800x600")
        self.home_callback = home_callback
        self.users_detail = users_detail

        self.conn = sqlite3.connect("FitZone.db")
        self.cursor = self.conn.cursor()

        self.manage_font = ManageFont()
        self.configure(background="#f2f2f2")

        self.add_new_member()
        self.create_registration_success_page()

    def create_registration_success_page(self):
        registration_success_frame = ttk.Frame(self, style="TFrame")
        registration_success_frame.pack(fill="both", expand=True, pady=160)

        success_label = ttk.Label(
            registration_success_frame,
            text="Registration Successful!",
            font=self.manage_font.large_bold_heading_font,
        )
        success_label.pack(pady=50)

        success_message = ttk.Label(
            registration_success_frame,
            text="Thank you for registering at FitZone. Your membership has been successfully created.",
            font=self.manage_font.medium_letters_font,
        )
        success_message.pack(pady=20)

        info_message = ttk.Label(
            registration_success_frame,
            text="You can now log in with your username and password to access all gym features.",
            font=self.manage_font.medium_letters_font,
        )
        info_message.pack(pady=10)

        self.back_button = tk.Button(
            registration_success_frame,
            text="Continue",
            width=100,
            background="#FFE4B5",
            foreground="#000000",
            font=self.manage_font.small_bold_heading_font,
        )
        self.back_button.pack(padx=10, pady=10)
        self.back_button.bind("<Button-1>", lambda event, func=self.home_callback: func())

    def add_new_member(self):
        try:
            insert_query = """
                INSERT INTO Members (LocationID, DurationID, PackageID, Username, Password, Salt,
                    Gender, Email, DateOfBirth, JoinDate, FirstName, LastName,
                    Address, CountryCode, PhoneNumber, ImagePath, EmailNotifications)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            member_data = (
                self.users_detail[0],   # LocationID
                self.users_detail[1],   # DurationID
                self.users_detail[2],   # PackageID
                self.users_detail[3],   # Username
                self.users_detail[4],   # Password
                self.users_detail[5],   # Salt
                self.users_detail[6],   # Gender
                self.users_detail[7],   # Email
                self.users_detail[8],   # DateOfBirth
                self.users_detail[9],   # JoinDate
                self.users_detail[10],  # FirstName
                self.users_detail[11],  # LastName
                self.users_detail[12],  # Address
                self.users_detail[13],  # CountryCode
                self.users_detail[14],  # PhoneNumber
                self.users_detail[15],  # ImagePath
                self.users_detail[16],  # EmailNotifications
            )
            self.cursor.execute(insert_query, member_data)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print("Error inserting member:", e)
            return False
        except IndexError as e:
            print("Data format error:", e)
            return False
