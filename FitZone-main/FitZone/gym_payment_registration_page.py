import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
from gym_font import ManageFont
from gym_function_bank import MessageHandler, ValidateCredentials
import datetime


class GymPaymentPage(GymBasePage):
    def __init__(self, membership_price, registration_success_callback):
        super().__init__()
        self.title("FitZone - Payment")
        self.geometry("800x600")
        self.registration_success_callback = registration_success_callback

        self.month_field = 0
        self.year_field = 0
        self.membership_price = str(membership_price)

        self.manage_font = ManageFont()
        self.validate_credentials = ValidateCredentials()
        self.message_handler = MessageHandler(self)

        self.error_string = []
        self.configure(background="#f2f2f2")
        self.create_payment_page()

    def create_payment_page(self):
        self.frame = ttk.Frame(self, style="TFrame")
        self.frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        payment_frame = ttk.Frame(self.scrollable_frame)
        payment_frame.pack(anchor="center", pady=120, fill=tk.Y)

        ttk.Label(payment_frame, text="Enter Payment Information", font=self.manage_font.large_bold_heading_font).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(payment_frame, text="Please enter your payment information to complete your gym membership.", font=self.manage_font.medium_letters_font).grid(row=1, column=0, columnspan=2, sticky=tk.W)

        price_totals_frame = tk.Frame(payment_frame, background="#333333", width=40)
        price_totals_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W)

        ttk.Label(price_totals_frame, text="Total Price: ", font=self.manage_font.smaller_letters_font, width=100, background="#333333", foreground="#FFFFFF").pack(anchor=tk.W, padx=10)
        ttk.Label(price_totals_frame, text="$" + self.membership_price, font=self.manage_font.large_bold_letters_font, background="#333333", foreground="#FFFFFF").pack(anchor=tk.W, padx=10)

        ttk.Label(payment_frame, text="Cardholder Name:", font=self.manage_font.medium_letters_font).grid(row=3, column=0, sticky=tk.W)
        self.cardholder_name_entry = ttk.Entry(payment_frame, font=self.manage_font.medium_letters_font, width=50)
        self.cardholder_name_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=5)

        ttk.Label(payment_frame, text="Card Number:", font=self.manage_font.medium_letters_font).grid(row=4, column=0, sticky=tk.W)
        self.card_number_entry = ttk.Entry(payment_frame, font=self.manage_font.medium_letters_font, width=50)
        self.card_number_entry.grid(row=4, column=1, columnspan=2, padx=10, pady=5)
        validate_card_number = self.register(self.check_numeric_input)
        self.card_number_entry.config(validate="key", validatecommand=(validate_card_number, "%P", 19))

        ttk.Label(payment_frame, text="Expiration Date: ", font=self.manage_font.medium_letters_font).grid(row=5, column=0, sticky=tk.W)
        self.expiration_year_entry = ttk.Entry(payment_frame, font=self.manage_font.medium_letters_font, width=10)
        self.expiration_year_entry.insert(0, "YYYY")
        self.expiration_year_entry.bind("<FocusIn>", self.on_entry_click)
        self.expiration_year_entry.grid(row=5, column=1, padx=10, pady=5)
        self.expiration_year_entry.config(foreground="#888888")
        validate_expiration_year = self.register(self.check_numeric_input)
        self.expiration_year_entry.config(validate="key", validatecommand=(validate_expiration_year, "%P", 4))

        self.expiration_month_entry = ttk.Entry(payment_frame, font=self.manage_font.medium_letters_font, width=10)
        self.expiration_month_entry.insert(0, "MM")
        self.expiration_month_entry.bind("<FocusIn>", self.on_entry_click)
        self.expiration_month_entry.grid(row=5, column=2, padx=10, pady=5)
        self.expiration_month_entry.config(foreground="#888888")
        validate_expiration_month = self.register(self.check_numeric_input)
        self.expiration_month_entry.config(validate="key", validatecommand=(validate_expiration_month, "%P", 2))

        ttk.Label(payment_frame, text="CVC:", font=self.manage_font.medium_letters_font).grid(row=6, column=0, sticky=tk.W)
        self.cvc_entry = ttk.Entry(payment_frame, font=self.manage_font.medium_letters_font, width=50)
        self.cvc_entry.grid(row=6, column=1, columnspan=2, padx=10, pady=5)
        validate_cvc = self.register(self.check_numeric_input)
        self.cvc_entry.config(validate="key", validatecommand=(validate_cvc, "%P", 3))

        self.submit_button = tk.Button(payment_frame, text="Submit Payment", background="#333333", foreground="#FFFFFF", font=self.manage_font.medium_letters_font, command=self.process_payment)
        self.submit_button.grid(row=7, columnspan=2, pady=10)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def process_payment(self):
        self.error_string = []
        self.cardholder_name = self.cardholder_name_entry.get()
        self.card_number = self.card_number_entry.get()
        self.expiration_month = self.expiration_month_entry.get()
        self.expiration_year = self.expiration_year_entry.get()
        self.cvc = self.cvc_entry.get()

        self.collect_all_invalid_and_empty_fields()
        self.destroy_error_messages()

        if self.error_string:
            self.display_error_messages(self.error_string)
        else:
            self.submit_button.bind("<Button-1>", lambda event, func=self.registration_success_callback: func())
            self.submit_button.event_generate("<Button-1>")

    def destroy_error_messages(self):
        try:
            self.error_frame.destroy()
        except Exception:
            pass

    def display_error_messages(self, error_string):
        self.error_frame = tk.Frame(self.scrollable_frame)
        self.error_frame.pack(anchor="center", fill=tk.Y)
        message_row = 0
        for message in error_string:
            message_row += 1
            error_message_frame = tk.Frame(self.error_frame, background="#D11A17")
            error_message_frame.grid(row=message_row, column=0, sticky=tk.W, pady=5)
            error_label = tk.Label(error_message_frame, text=message, font=self.manage_font.medium_letters_font, background="#D11A17", foreground="#FFFFFF", width=70)
            error_label.pack()
            close_button = tk.Button(error_message_frame, text="\u2716", background="#D11A17", foreground="#FFFFFF", command=lambda frame=error_message_frame: frame.destroy())
            close_button.pack(side="right")

    def collect_all_invalid_and_empty_fields(self):
        empty_fields = []
        self.error_string = []

        if not self.cardholder_name:
            empty_fields.append("Cardholder Name")
        if not self.card_number:
            empty_fields.append("Card Number")
        if self.month_field != 1 or not self.expiration_month:
            empty_fields.append("Expiration Month")
        if self.year_field != 1 or not self.expiration_year:
            empty_fields.append("Expiration Year")
        if not self.cvc:
            empty_fields.append("CVC")

        for fields in empty_fields:
            self.error_string.append(f"Error: \u26A0 Please enter {fields}.")

        self.empty_string_error = empty_fields

        if not self.empty_string_error:
            self.collect_all_invalid_fields()

    def collect_all_invalid_fields(self):
        try:
            if not self.cardholder_name.replace(" ", "").isalpha():
                self.error_string.append("Error: \u26A0 Cardholder Name must contain only letters and spaces")
        except ValueError:
            self.error_string.append("Error: \u26A0 Invalid input for Cardholder Name")

        try:
            if len(self.card_number) < 16:
                self.error_string.append("Error: \u26A0 Please input a valid Card Number")
        except ValueError:
            self.error_string.append("Error: \u26A0 Invalid input for Card Number")

        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month

        try:
            if not self.empty_string_error and len(self.expiration_year) != 4:
                self.error_string.append("Error: \u26A0 Expiration Year must be 4 digits")
        except ValueError:
            self.error_string.append("Error: \u26A0 Invalid input for Expiration Year")

        try:
            if not self.empty_string_error and len(self.expiration_month) != 2:
                self.error_string.append("Error: \u26A0 Expiration Month must be 2 digits")
        except ValueError:
            self.error_string.append("Error: \u26A0 Invalid input for Expiration Month")

        try:
            if not self.empty_string_error and (
                int(self.expiration_year) < current_year
                or (int(self.expiration_year) == current_year and int(self.expiration_month) < current_month)
            ):
                self.error_string.append("Error: \u26A0 Card has expired. Please check the Expiration Date")
        except ValueError:
            self.error_string.append("Error: \u26A0 Invalid input for Expiration Year or Month")

        try:
            if not self.empty_string_error and int(self.expiration_year) > current_year + 5:
                self.error_string.append("Error: \u26A0 Expiration Date is too far in the future.")
        except ValueError:
            self.error_string.append("Error: \u26A0 Invalid input for Expiration Year or Month")

        try:
            if not self.empty_string_error:
                exp_month_int = int(self.expiration_month)
                if exp_month_int < 1 or exp_month_int > 12:
                    self.error_string.append("Error: \u26A0 Expiration Month must be between 1 and 12")
        except ValueError:
            self.error_string.append("Error: \u26A0 Invalid input for Expiration Month")

        try:
            if len(self.cvc) != 3 and not self.empty_string_error:
                self.error_string.append("Error: \u26A0 Please input a valid CVC")
        except ValueError:
            self.error_string.append("Error: \u26A0 Invalid input for CVC")

    def on_entry_click(self, event):
        entry = event.widget
        if entry.get() == "YYYY":
            self.year_field = 1
            entry.delete(0, "end")
            entry.insert(0, "")
            entry.config(foreground="black")
        elif entry.get() == "MM":
            self.month_field = 1
            entry.delete(0, "end")
            entry.insert(0, "")
            entry.config(foreground="black")

    def check_numeric_input(self, string, length):
        return (string.isdigit() or string == "") and len(string) <= int(length)
