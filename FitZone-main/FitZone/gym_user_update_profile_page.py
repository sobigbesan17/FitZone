import os
import sqlite3
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk, filedialog
from tkcalendar import DateEntry
from gym_font import ManageFont
from gym_function_bank import MessageHandler, ValidateCredentials, PasswordHandler
from PIL import Image, ImageTk
from pathlib import Path
import datetime


class GymUpdateProfilePage(GymBasePage):
    def __init__(self, member_id, home_callback, profile_updated_callback=None):
        super().__init__()
        self.title("FitZone - Update Profile")
        self.geometry("800x700")
        self.member_id = member_id
        self.home_callback = home_callback
        self.profile_updated_callback = profile_updated_callback

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)
        self.validate_credentials = ValidateCredentials()
        self.password_handler = PasswordHandler()

        self.conn = sqlite3.connect("FitZone.db")
        self.cursor = self.conn.cursor()

        self.member_data = {}
        self.image_path = ""
        self.show_password = tk.BooleanVar(value=False)

        self.configure(background="#f2f2f2")
        self.load_member_data()
        self.create_update_profile_page()

    def load_member_data(self):
        try:
            self.cursor.execute(
                """SELECT Username, Gender, Email, DateOfBirth, FirstName, LastName,
                          Address, CountryCode, PhoneNumber, ImagePath, EmailNotifications
                   FROM Members WHERE MemberID = ?""",
                (self.member_id,)
            )
            result = self.cursor.fetchone()
            if result:
                keys = ["Username", "Gender", "Email", "DateOfBirth", "FirstName", "LastName",
                        "Address", "CountryCode", "PhoneNumber", "ImagePath", "EmailNotifications"]
                self.member_data = dict(zip(keys, result))
        except sqlite3.Error as e:
            print("Error loading member data:", e)

    def create_update_profile_page(self):
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

        tk.Label(content, text="Update Your Profile", font=self.manage_font.large_bold_heading_font).pack(anchor=tk.W)
        tk.Label(content, text="Edit your personal details below.",
                 font=self.manage_font.medium_letters_font).pack(anchor=tk.W, pady=(0, 20))

        form_frame = tk.Frame(content)
        form_frame.pack(fill=tk.X)

        row = 0

        def add_row(label_text, widget):
            nonlocal row
            tk.Label(form_frame, text=label_text, font=self.manage_font.medium_bold_letters_font).grid(
                row=row, column=0, sticky=tk.W, padx=10, pady=5
            )
            widget.grid(row=row, column=1, padx=10, pady=5, sticky=tk.W)
            row += 1

        tk.Label(form_frame, text="First Name:", font=self.manage_font.medium_bold_letters_font).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.first_name_entry = ttk.Entry(form_frame, font=self.manage_font.medium_letters_font, width=50)
        self.first_name_entry.insert(0, self.member_data.get("FirstName", ""))
        self.first_name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Last Name:", font=self.manage_font.medium_bold_letters_font).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.last_name_entry = ttk.Entry(form_frame, font=self.manage_font.medium_letters_font, width=50)
        self.last_name_entry.insert(0, self.member_data.get("LastName", ""))
        self.last_name_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Email:", font=self.manage_font.medium_bold_letters_font).grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.email_entry = ttk.Entry(form_frame, font=self.manage_font.medium_letters_font, width=50)
        self.email_entry.insert(0, self.member_data.get("Email", ""))
        self.email_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Gender:", font=self.manage_font.medium_bold_letters_font).grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        self.gender_var = tk.StringVar(value=self.member_data.get("Gender", "Female"))
        gender_combo = ttk.Combobox(
            form_frame,
            textvariable=self.gender_var,
            values=["Female", "Male", "Other"],
            state="readonly",
            width=47,
            font=self.manage_font.medium_letters_font,
        )
        gender_combo.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Date of Birth:", font=self.manage_font.medium_bold_letters_font).grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        self.dob_entry = DateEntry(form_frame, font=self.manage_font.medium_letters_font, width=47, date_pattern="yyyy-mm-dd")
        dob_val = self.member_data.get("DateOfBirth", "")
        if dob_val:
            try:
                self.dob_entry.set_date(dob_val)
            except Exception:
                pass
        self.dob_entry.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Address:", font=self.manage_font.medium_bold_letters_font).grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        self.address_entry = ttk.Entry(form_frame, font=self.manage_font.medium_letters_font, width=50)
        self.address_entry.insert(0, self.member_data.get("Address", ""))
        self.address_entry.grid(row=5, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Country Code:", font=self.manage_font.medium_bold_letters_font).grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
        self.country_code_var = tk.StringVar(value=self.member_data.get("CountryCode", "+44"))
        country_codes = ["+44", "+1", "+61", "+91", "+33", "+49", "+81", "+86"]
        country_code_combo = ttk.Combobox(
            form_frame,
            textvariable=self.country_code_var,
            values=country_codes,
            width=47,
            font=self.manage_font.medium_letters_font,
        )
        country_code_combo.grid(row=6, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Phone Number:", font=self.manage_font.medium_bold_letters_font).grid(row=7, column=0, sticky=tk.W, padx=10, pady=5)
        self.phone_entry = ttk.Entry(form_frame, font=self.manage_font.medium_letters_font, width=50)
        self.phone_entry.insert(0, self.member_data.get("PhoneNumber", ""))
        self.phone_entry.grid(row=7, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="New Password:", font=self.manage_font.medium_bold_letters_font).grid(row=8, column=0, sticky=tk.W, padx=10, pady=5)
        self.new_password_entry = ttk.Entry(form_frame, font=self.manage_font.medium_letters_font, width=50, show="*")
        self.new_password_entry.grid(row=8, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Profile Image:", font=self.manage_font.medium_bold_letters_font).grid(row=9, column=0, sticky=tk.W, padx=10, pady=5)
        upload_btn = tk.Button(
            form_frame, text="Upload New Image",
            font=self.manage_font.medium_letters_font,
            background="#333333", foreground="#FFFFFF",
            command=self.upload_image
        )
        upload_btn.grid(row=9, column=1, padx=10, pady=5, sticky=tk.W)

        self.profile_preview_width = 220
        self.profile_preview_height = 220
        self.profile_photo = None
        placeholder_image = Image.new(
            "RGB",
            (self.profile_preview_width, self.profile_preview_height),
            (242, 242, 242),
        )
        self.profile_photo_placeholder = ImageTk.PhotoImage(placeholder_image)
        self.profile_image_preview = tk.Label(
            form_frame,
            image=self.profile_photo_placeholder,
            text="No image selected",
            compound="center",
            font=self.manage_font.smaller_letters_font,
            background="#f2f2f2",
            bd=1,
            relief=tk.SOLID,
            width=self.profile_preview_width,
            height=self.profile_preview_height,
            anchor="center",
        )
        self.profile_image_preview.grid(row=10, column=1, padx=10, pady=5, sticky=tk.W)

        self.original_image_path = self.member_data.get("ImagePath", "")
        self.image_path = ""
        self.image_label = tk.Label(
            form_frame,
            text="No image selected",
            font=self.manage_font.smaller_letters_font,
        )
        self.image_label.grid(row=11, column=1, padx=10, sticky=tk.W)

        self.email_notifications = tk.BooleanVar(value=bool(self.member_data.get("EmailNotifications", True)))
        tk.Checkbutton(
            form_frame, text="Receive email notifications",
            font=self.manage_font.medium_letters_font,
            variable=self.email_notifications
        ).grid(row=12, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)

        tk.Button(
            content, text="Save Changes",
            font=self.manage_font.medium_bold_letters_font,
            background="#4CAF50", foreground="#FFFFFF",
            command=self.save_changes
        ).pack(pady=20)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def upload_image(self):
        file_types = [("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        path = filedialog.askopenfilename(title="Select Profile Image", filetypes=file_types)
        if path:
            self.image_path = path
            self.image_label.config(text=os.path.basename(path))
            self._display_uploaded_image(path)

    def _resolve_image_path(self, image_path):
        if os.path.isabs(image_path) and os.path.exists(image_path):
            return image_path
        candidate = os.path.join(os.getcwd(), image_path)
        if os.path.exists(candidate):
            return candidate
        candidate = os.path.join(Path(__file__).resolve().parent, image_path)
        if os.path.exists(candidate):
            return candidate
        return None

    def _display_uploaded_image(self, image_path):
        try:
            image = Image.open(image_path)
            image = image.convert("RGB")
            target_width = self.profile_preview_width
            target_height = self.profile_preview_height
            ratio = min(target_width / image.width, target_height / image.height)
            resized_size = (max(1, int(image.width * ratio)), max(1, int(image.height * ratio)))
            resized_image = image.resize(resized_size, Image.LANCZOS)

            background = Image.new("RGB", (target_width, target_height), (242, 242, 242))
            x_offset = (target_width - resized_size[0]) // 2
            y_offset = (target_height - resized_size[1]) // 2
            background.paste(resized_image, (x_offset, y_offset))

            self.profile_photo = ImageTk.PhotoImage(background)
            self.profile_image_preview.config(image=self.profile_photo, text="")
        except Exception:
            self.profile_image_preview.config(text=os.path.basename(image_path), image=self.profile_photo_placeholder)

    def save_changes(self):
        errors = []
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        email = self.email_entry.get().strip()
        gender = self.gender_var.get()
        dob = self.dob_entry.get()
        address = self.address_entry.get().strip()
        country_code = self.country_code_var.get()
        phone = self.phone_entry.get().strip()
        new_password = self.new_password_entry.get()

        if not first_name:
            errors.append("Please enter your first name.")
        if not last_name:
            errors.append("Please enter your last name.")

        email_error = self.validate_credentials.validate_email(email)
        if email_error:
            errors.append(email_error)

        dob_error = self.validate_credentials.validate_date_of_birth(dob)
        if dob_error:
            errors.append(dob_error)

        phone_error = self.validate_credentials.validate_phone_number(phone)
        if phone_error:
            errors.append(phone_error)

        if new_password:
            pwd_error = self.validate_credentials.validate_password(new_password, 0)
            if isinstance(pwd_error, str) and pwd_error:
                errors.append(pwd_error)

        if errors:
            self.message_handler.invalid_message("Error: \n\n \u26A0 " + "\n \u26A0 ".join(errors))
            return

        try:
            image_path_to_save = self.image_path if self.image_path else self.original_image_path
            self.cursor.execute(
                """UPDATE Members SET FirstName=?, LastName=?, Email=?, Gender=?, DateOfBirth=?,
                   Address=?, CountryCode=?, PhoneNumber=?, ImagePath=?, EmailNotifications=?
                   WHERE MemberID=?""",
                (first_name, last_name, email, gender, dob, address, country_code,
                 phone, image_path_to_save, int(self.email_notifications.get()), self.member_id)
            )

            if new_password:
                hashed, salt = self.password_handler.hash_and_store_password(new_password)
                self.cursor.execute(
                    "UPDATE Members SET Password=?, Salt=? WHERE MemberID=?",
                    (hashed, salt, self.member_id)
                )

            self.conn.commit()
            self.image_path = image_path_to_save
            if callable(getattr(self, "profile_updated_callback", None)):
                try:
                    self.profile_updated_callback(self.image_path)
                except Exception:
                    pass
            try:
                self.refresh_header()
            except Exception:
                pass
            self.message_handler.success_message("Success: \n\n \u2705 Profile updated successfully!")
        except sqlite3.Error as e:
            self.message_handler.invalid_message(f"Error: \n\n \u26A0 Could not update profile: {e}")
