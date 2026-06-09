import io
import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk, filedialog
from tkcalendar import DateEntry
from PIL import Image, ImageTk
from gym_font import ManageFont
from gym_function_bank import MessageHandler, ValidateCredentials, PasswordHandler
from gym_captcha_verification import CaptchaVerification
import datetime


class GymDetailsRegistrationPage(GymBasePage):
    def __init__(self, payment_registration_callback):
        super().__init__()
        self.title("FitZone - User Details")
        self.geometry("800x600")
        self.payment_registration_callback = payment_registration_callback

        self.manage_font = ManageFont()
        self.password_handler = PasswordHandler()
        self.validate_credentials = ValidateCredentials()
        self.message_handler = MessageHandler(self)
        self.captcha_validation = CaptchaVerification()
        self.captcha_placeholder = "Enter CAPTCHA here"

        self.show_password = tk.BooleanVar(value=False)
        self.agreed_terms_and_conditions = tk.BooleanVar(value=False)
        self.email_notifications = tk.BooleanVar(value=False)

        self.image_path = ""
        self.error_string = []

        self.username = ""
        self.password = ""
        self.gender = "Female"
        self.email = ""
        self.date_of_birth = ""
        self.first_name = ""
        self.last_name = ""
        self.address = ""
        self.country_code = "+44"
        self.phone_number = ""

        self.configure(background="#f2f2f2")
        self.create_gym_details_page()

    def create_gym_details_page(self):
        self.frame = ttk.Frame(self, style="TFrame")
        self.frame.pack(fill="both", expand=True)
        gender_var = "Female"

        canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.gym_details_frame = ttk.Frame(self.scrollable_frame)
        self.gym_details_frame.pack(anchor="center", fill=tk.Y, pady=120)

        ttk.Label(
            self.gym_details_frame,
            text="Enter User Details",
            font=self.manage_font.large_bold_heading_font,
        ).grid(row=0, column=0, sticky=tk.W)

        ttk.Label(
            self.gym_details_frame,
            text="Please enter your personal information to create your gym account.",
            font=self.manage_font.medium_letters_font,
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W)

        ttk.Label(self.gym_details_frame, text="First Name:", font=self.manage_font.medium_letters_font).grid(row=2, column=0, sticky=tk.W)
        self.first_name_entry = ttk.Entry(self.gym_details_frame, font=self.manage_font.medium_letters_font, width=50)
        self.first_name_entry.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(self.gym_details_frame, text="Last Name:", font=self.manage_font.medium_letters_font).grid(row=3, column=0, sticky=tk.W)
        self.last_name_entry = ttk.Entry(self.gym_details_frame, font=self.manage_font.medium_letters_font, width=50)
        self.last_name_entry.grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(self.gym_details_frame, text="Username:", font=self.manage_font.medium_letters_font).grid(row=4, column=0, sticky=tk.W)
        self.username_entry = ttk.Entry(self.gym_details_frame, font=self.manage_font.medium_letters_font, width=50)
        self.username_entry.grid(row=4, column=1, padx=10, pady=5)

        ttk.Label(self.gym_details_frame, text="Password:", font=self.manage_font.medium_letters_font).grid(row=5, column=0, sticky=tk.W)
        self.password_entry = ttk.Entry(self.gym_details_frame, show="*", font=self.manage_font.medium_letters_font, width=50)
        self.password_entry.grid(row=5, column=1, padx=10, pady=5)

        show_password_checkbox = tk.Checkbutton(
            self.gym_details_frame,
            text="Show Password",
            font=self.manage_font.medium_letters_font,
            variable=self.show_password,
            command=self.toggle_password_visibility,
        )
        show_password_checkbox.grid(row=5, column=2, padx=10, pady=5, sticky=tk.W)

        ttk.Label(self.gym_details_frame, text="Email Address:", font=self.manage_font.medium_letters_font).grid(row=6, column=0, sticky=tk.W)
        self.email_entry = ttk.Entry(self.gym_details_frame, font=self.manage_font.medium_letters_font, width=50)
        self.email_entry.grid(row=6, column=1, padx=10, pady=5)

        ttk.Label(self.gym_details_frame, text="Date of Birth:", font=self.manage_font.medium_letters_font).grid(row=7, column=0, sticky=tk.W)
        self.dob_entry = DateEntry(self.gym_details_frame, font=self.manage_font.medium_letters_font, width=47, date_pattern="yyyy-mm-dd")
        self.dob_entry.grid(row=7, column=1, padx=10, pady=5)

        ttk.Label(self.gym_details_frame, text="Gender:", font=self.manage_font.medium_letters_font).grid(row=8, column=0, sticky=tk.W)
        self.gender_var = tk.StringVar(value="Female")
        gender_menu = ttk.Combobox(
            self.gym_details_frame,
            textvariable=self.gender_var,
            values=["Female", "Male", "Other"],
            state="readonly",
            width=47,
            font=self.manage_font.medium_letters_font,
        )
        gender_menu.grid(row=8, column=1, padx=10, pady=5)

        ttk.Label(self.gym_details_frame, text="Address:", font=self.manage_font.medium_letters_font).grid(row=9, column=0, sticky=tk.W)
        self.address_entry = ttk.Entry(self.gym_details_frame, font=self.manage_font.medium_letters_font, width=50)
        self.address_entry.grid(row=9, column=1, padx=10, pady=5)

        ttk.Label(self.gym_details_frame, text="Country Code:", font=self.manage_font.medium_letters_font).grid(row=10, column=0, sticky=tk.W)
        self.country_code_var = tk.StringVar(value="+44")
        country_codes = ["+44", "+1", "+61", "+91", "+33", "+49", "+81", "+86"]
        country_code_menu = ttk.Combobox(
            self.gym_details_frame,
            textvariable=self.country_code_var,
            values=country_codes,
            width=47,
            font=self.manage_font.medium_letters_font,
        )
        country_code_menu.grid(row=10, column=1, padx=10, pady=5)

        ttk.Label(self.gym_details_frame, text="Phone Number:", font=self.manage_font.medium_letters_font).grid(row=11, column=0, sticky=tk.W)
        self.phone_entry = ttk.Entry(self.gym_details_frame, font=self.manage_font.medium_letters_font, width=50)
        validate_phone = self.register(self.check_numeric_input)
        self.phone_entry.config(validate="key", validatecommand=(validate_phone, "%P", 10))
        self.phone_entry.grid(row=11, column=1, padx=10, pady=5)

        ttk.Label(self.gym_details_frame, text="Profile Image:", font=self.manage_font.medium_letters_font).grid(row=12, column=0, sticky=tk.W)
        upload_btn = tk.Button(
            self.gym_details_frame, text="Upload Image",
            font=self.manage_font.medium_letters_font,
            background="#333333", foreground="#FFFFFF",
            command=self.upload_image,
        )
        upload_btn.grid(row=12, column=1, padx=10, pady=5, sticky=tk.W)

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
            self.gym_details_frame,
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
        self.profile_image_preview.grid(row=13, column=1, padx=10, pady=5, sticky=tk.W)

        tk.Checkbutton(
            self.gym_details_frame,
            text="I agree to the Terms and Conditions",
            font=self.manage_font.medium_letters_font,
            variable=self.agreed_terms_and_conditions,
        ).grid(row=14, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)

        tk.Checkbutton(
            self.gym_details_frame,
            text="I would like to receive email notifications",
            font=self.manage_font.medium_letters_font,
            variable=self.email_notifications,
        ).grid(row=15, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)

        self.captcha_validation.generate_captcha()
        self.captcha_image = ImageTk.PhotoImage(self.captcha_validation.get_captcha_image())
        self.captcha_image_label = tk.Label(
            self.gym_details_frame,
            image=self.captcha_image,
            background="#f2f2f2",
            bd=2,
            relief=tk.SOLID,
        )
        self.captcha_image_label.grid(row=16, column=0, sticky=tk.W, padx=10, pady=5)

        refresh_captcha_btn = tk.Button(
            self.gym_details_frame,
            text="Refresh CAPTCHA",
            font=self.manage_font.medium_letters_font,
            background="#444444",
            foreground="#FFFFFF",
            command=self.refresh_captcha,
        )
        refresh_captcha_btn.grid(row=16, column=1, sticky=tk.W, padx=10, pady=5)

        self.captcha_entry = tk.Entry(
            self.gym_details_frame,
            font=self.manage_font.medium_letters_font,
            width=50,
            bd=2,
            relief=tk.SOLID,
            fg="#888888",
        )
        self.captcha_entry.insert(0, self.captcha_placeholder)
        self.captcha_entry.bind("<FocusIn>", self.on_entry_click)
        self.captcha_entry.bind("<FocusOut>", self.on_entry_focus_out)
        self.captcha_entry.grid(row=17, column=0, columnspan=2, padx=10, pady=5)

        submit_btn = tk.Button(
            self.gym_details_frame,
            text="Submit",
            font=self.manage_font.medium_letters_font,
            background="#333333", foreground="#FFFFFF",
            command=self.validate_and_submit,
        )
        submit_btn.grid(row=18, column=0, columnspan=3, pady=20)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def upload_image(self):
        file_types = [("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        image_path = filedialog.askopenfilename(title="Select Profile Image", filetypes=file_types)
        if image_path:
            self.image_path = image_path
            self._display_uploaded_image(image_path)

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
            self.profile_image_preview.config(text=image_path.split("/")[-1], image=self.profile_photo_placeholder)

    def toggle_password_visibility(self):
        if self.show_password.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
        self.password_entry.focus_set()

    def check_numeric_input(self, string, length):
        return (string.isdigit() or string == "") and len(string) <= int(length)

    def on_entry_click(self, event):
        entry = event.widget
        if entry.get() == self.captcha_placeholder:
            entry.delete(0, "end")
            entry.config(fg="black")

    def on_entry_focus_out(self, event):
        entry = event.widget
        if not entry.get().strip():
            entry.delete(0, "end")
            entry.insert(0, self.captcha_placeholder)
            entry.config(fg="#888888")

    def refresh_captcha(self):
        self.captcha_validation.generate_captcha()
        new_image = ImageTk.PhotoImage(self.captcha_validation.get_captcha_image())
        self.captcha_image = new_image
        self.captcha_image_label.config(image=self.captcha_image)
        self.captcha_entry.delete(0, tk.END)
        self.captcha_entry.insert(0, self.captcha_placeholder)
        self.captcha_entry.config(fg="#888888")

    def validate_and_submit(self):
        self.error_string = []

        self.first_name = self.first_name_entry.get().strip()
        self.last_name = self.last_name_entry.get().strip()
        self.username = self.username_entry.get().strip()
        self.password = self.password_entry.get()
        self.email = self.email_entry.get().strip()
        self.date_of_birth = self.dob_entry.get()
        self.gender = self.gender_var.get()
        self.address = self.address_entry.get().strip()
        self.country_code = self.country_code_var.get()
        self.phone_number = self.phone_entry.get().strip()

        if not self.first_name:
            self.error_string.append("Please enter your first name.")
        if not self.last_name:
            self.error_string.append("Please enter your last name.")

        username_error = self.validate_credentials.validate_username(self.username)
        if username_error:
            self.error_string.append(username_error)

        password_error = self.validate_credentials.validate_password(self.password, 0)
        if isinstance(password_error, str) and password_error:
            self.error_string.append(password_error)

        email_error = self.validate_credentials.validate_email(self.email)
        if email_error:
            self.error_string.append(email_error)

        dob_error = self.validate_credentials.validate_date_of_birth(self.date_of_birth)
        if dob_error:
            self.error_string.append(dob_error)

        phone_error = self.validate_credentials.validate_phone_number(self.phone_number)
        if phone_error:
            self.error_string.append(phone_error)

        captcha_input = self.captcha_entry.get().strip()
        if captcha_input == self.captcha_placeholder or not captcha_input:
            self.error_string.append("Please enter the CAPTCHA text.")
        elif not self.captcha_validation.verify_captcha(captcha_input):
            self.error_string.append("Invalid CAPTCHA. Please try again.")

        if not self.agreed_terms_and_conditions.get():
            self.error_string.append("Please agree to the Terms and Conditions.")

        if self.error_string:
            error_text = "Error: \n\n " + "\n \u26A0 ".join(self.error_string)
            self.message_handler.invalid_message(error_text)
        else:
            self.message_handler.success_message("Success: \n\n \u2705 Details validated successfully!")
            self.after(500, self.payment_registration_callback)

    def get_user_account_details(self):
        password_hash, salt = self.password_handler.hash_and_store_password(self.password)
        join_date = datetime.datetime.now().date()
        email_notifications_value = int(self.email_notifications.get())
        return [
            self.username, password_hash, salt, self.gender, self.email,
            self.date_of_birth, join_date, self.first_name, self.last_name,
            self.address, self.country_code, self.phone_number,
            self.image_path, email_notifications_value,
        ]
