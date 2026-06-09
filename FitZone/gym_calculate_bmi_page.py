import tkinter as tk
from gym_page_base import GymBasePage
from tkinter import ttk
from gym_font import ManageFont
from gym_function_bank import MessageHandler, ReadText
import sqlite3
import datetime


class CalculateBMIPage(GymBasePage):
    def __init__(self, member_id, fitness_dashboard_callback, calculate_bmi_callback,
                 bmi_visualisation_callback, gym_meal_planner_callback,
                 gym_workout_planner_callback, view_class_schedule_callback,
                 gym_class_booking_callback, gym_class_clashes_callback):
        super().__init__()
        self.title("Fitness Dashboard")
        self.geometry("1000x700")
        self.member_id = member_id

        self.manage_font = ManageFont()
        self.message_handler = MessageHandler(self)

        self.bmi_educational_frame = None
        self.bmi_category = None

        self.create_bmi_calculator()
        self.create_bmi_reference_table()

    def create_bmi_calculator(self):
        self.bmi_top_frame = ttk.Frame(self)
        self.bmi_top_frame.pack()

        bmi_frame = ttk.Frame(self.bmi_top_frame)
        bmi_frame.pack(fill="both", expand=True, side="left", padx=60)

        bmi_label = tk.Label(bmi_frame, text="Calculate BMI", font=self.manage_font.heading_font)
        bmi_label.pack(pady=(20, 10))

        measurement_system_label = tk.Label(bmi_frame, text="Select Measurement System:", font=self.manage_font.medium_bold_letters_font)
        measurement_system_label.pack()

        self.measurement_system_var = tk.StringVar()
        self.measurement_system_var.set("Metric")
        measurement_system_menu = ttk.Combobox(
            bmi_frame, font=self.manage_font.medium_letters_font,
            textvariable=self.measurement_system_var,
            values=["Metric", "Imperial"], state="readonly"
        )
        measurement_system_menu.pack()

        weight_label_text = tk.StringVar()
        height_label_text = tk.StringVar()

        weight_label = tk.Label(bmi_frame, textvariable=weight_label_text, font=self.manage_font.medium_bold_letters_font)
        weight_label.pack()

        self.update_measurement_labels(weight_label_text, height_label_text)

        self.weight_entry = tk.Entry(bmi_frame, font=self.manage_font.medium_letters_font)
        self.weight_entry.pack()
        validate_weight = self.register(self.check_numeric_input)
        self.weight_entry.config(validate="key", validatecommand=(validate_weight, "%P", 4))

        height_label = tk.Label(bmi_frame, textvariable=height_label_text, font=self.manage_font.medium_bold_letters_font)
        height_label.pack()

        self.height_entry = tk.Entry(bmi_frame, font=self.manage_font.medium_letters_font)
        self.height_entry.pack()
        validate_height = self.register(self.check_numeric_input)
        self.height_entry.config(validate="key", validatecommand=(validate_height, "%P", 4))

        calculate_button = tk.Button(
            bmi_frame, text="Calculate",
            font=self.manage_font.medium_bold_heading_font,
            background="#FFE4B5", width=30, command=self.calculate_bmi
        )
        calculate_button.pack(pady=(10, 20))

        self.bmi_result_label = tk.Label(bmi_frame, text="", font=self.manage_font.medium_bold_heading_font)
        self.bmi_result_label.pack()

        measurement_system_menu.bind(
            "<<ComboboxSelected>>",
            lambda event, w=weight_label_text, h=height_label_text: self.update_measurement_labels(w, h)
        )

    def update_measurement_labels(self, weight_label_text, height_label_text):
        if self.measurement_system_var.get() == "Imperial":
            weight_label_text.set("Enter Weight (lbs):")
            height_label_text.set("Enter Height (inches):")
        else:
            weight_label_text.set("Enter Weight (kg):")
            height_label_text.set("Enter Height (cm):")

    def calculate_bmi(self):
        try:
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())

            if self.measurement_system_var.get() == "Imperial":
                weight = weight * 0.453592
                height = height * 0.0254
            else:
                height = height / 100

            bmi = weight / (height ** 2)

            result_text = f"Your BMI is: {bmi:.2f}"
            self.bmi_category = self.get_bmi_category(bmi)
            result_text += f" ({self.bmi_category})"

            self.bmi_result_label.config(text=result_text)
            self.display_educational_bmi_information()

        except ValueError:
            if not self.weight_entry.get() and not self.height_entry.get():
                self.bmi_result_label.config(text="Please enter valid weight and height.")
            elif not self.weight_entry.get():
                self.bmi_result_label.config(text="Please enter valid weight.")
            elif not self.height_entry.get():
                self.bmi_result_label.config(text="Please enter valid height.")
            else:
                self.bmi_result_label.config(text="Please enter numeric values for weight and height.")

    def display_educational_bmi_information(self):
        if self.bmi_educational_frame:
            self.bmi_educational_frame.destroy()

        self.bmi_educational_frame = tk.Frame(self)
        self.bmi_educational_frame.pack()

        self.bmi_description_frame = tk.Frame(self.bmi_educational_frame, background="#333333")
        self.bmi_description_frame.pack()

        file_path = "EducationalBMIInformation.txt"
        read_text = ReadText(file_path)
        description_title = self.bmi_category + " Description:"
        bmi_educational_description = read_text.extract_description(description_title)

        educational_bmi_title = tk.Label(
            self.bmi_description_frame, text=description_title,
            background="#333333", foreground="white",
            font=self.manage_font.medium_bold_heading_font
        )
        educational_bmi_title.pack(pady=(20, 10))

        bmi_educational_text = tk.Text(
            self.bmi_description_frame, background="#333333", foreground="white",
            height=10, font=self.manage_font.medium_bold_letters_font
        )
        bmi_educational_text.pack(fill="both", expand=True)
        bmi_educational_text.insert("1.0", bmi_educational_description)
        bmi_educational_text.config(state="disabled")

        insert_bmi_button = tk.Button(
            self.bmi_educational_frame, text="Insert BMI",
            font=self.manage_font.medium_bold_heading_font,
            background="#C80000", width=30, command=self.insert_bmi
        )
        insert_bmi_button.pack(pady=(10, 20))

    def insert_bmi(self):
        try:
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())
            measurement_system = self.measurement_system_var.get()

            if measurement_system == "Imperial":
                weight_kg = weight * 0.453592
                height_m = height * 0.0254
            else:
                weight_kg = weight
                height_m = height / 100

            bmi = weight_kg / (height_m ** 2)
            bmi_category = self.get_bmi_category(bmi)
            date_recorded = datetime.date.today()

            conn = sqlite3.connect("FitZone.db")
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO BMIRecords (MemberID, Weight, Height, BMI, BMICategory, DateRecorded, MeasurementSystem)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (self.member_id, weight, height, round(bmi, 2), bmi_category, date_recorded, measurement_system)
            )
            conn.commit()
            conn.close()
            self.message_handler.success_message("Success: \n\n \u2705 BMI recorded successfully!")
        except Exception as e:
            self.message_handler.invalid_message(f"Error: \n\n \u26A0 Could not insert BMI: {e}")

    def get_bmi_category(self, bmi):
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 24.9:
            return "Normal Weight"
        elif 24.9 <= bmi < 29.9:
            return "Overweight"
        elif bmi >= 29.9:
            if bmi < 34.9:
                return "Obese (Class 1)"
            elif bmi < 39.9:
                return "Obese (Class 2)"
            else:
                return "Obese (Class 3)"

    def check_numeric_input(self, string, length):
        return (string.replace(".", "", 1).isdigit() or string == "") and len(string) <= int(length)

    def create_bmi_reference_table(self):
        reference_frame = ttk.Frame(self.bmi_top_frame)
        reference_frame.pack(fill="both", expand=True, side="right")

        reference_label = tk.Label(reference_frame, text="BMI Reference Table", font=self.manage_font.heading_font)
        reference_label.pack(pady=(20, 10))

        tree_style = ttk.Style()
        tree_style.configure("Treeview", font=self.manage_font.medium_letters_font)
        tree_style.configure("Treeview.Heading", font=self.manage_font.medium_bold_letters_font)

        bmi_table = ttk.Treeview(reference_frame, columns=("BMI Category", "BMI Range", "Health Risk"), show="headings")
        bmi_table.heading("BMI Category", text="BMI Category")
        bmi_table.heading("BMI Range", text="BMI Range")
        bmi_table.heading("Health Risk", text="Health Risk")

        bmi_data = [
            ("Underweight", "Below 18.5", "Nutritional deficiency"),
            ("Normal Weight", "18.5 - 24.9", "Low"),
            ("Overweight", "25 - 29.9", "Moderate"),
            ("Obese (Class 1)", "30 - 34.9", "High"),
            ("Obese (Class 2)", "35 - 39.9", "Very High"),
            ("Obese (Class 3)", "40 and above", "Extremely High"),
        ]

        colors = ["#D6EAF8", "#D5F5E3", "#FDEBD0", "#FADBD8", "#E8DAEF", "#FDFEFE"]
        for i, (bmi_category, bmi_range, health_risk) in enumerate(bmi_data):
            bmi_table.insert("", "end", values=(bmi_category, bmi_range, health_risk), tags=(colors[i],))
            bmi_table.tag_configure(colors[i], background=colors[i])

        bmi_table.pack(fill="both", expand=True, padx=20, pady=20)
