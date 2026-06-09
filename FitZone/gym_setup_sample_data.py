import sqlite3
import csv
import os


def setup_sample_data():
    conn = sqlite3.connect("FitZone.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM GymLocations")
    if cursor.fetchone()[0] == 0:
        locations = [
            ("FitZone Central", "123 Main Street, London, EC1A 1BB", "central@fitzone.co.uk", "0207123456", "Our flagship central London gym with state-of-the-art facilities."),
            ("FitZone North", "456 High Road, Manchester, M1 1AE", "north@fitzone.co.uk", "0161234567", "A premium gym in the heart of Manchester city centre."),
            ("FitZone South", "789 Station Road, Birmingham, B1 1TA", "south@fitzone.co.uk", "0121345678", "A spacious modern gym serving South Birmingham."),
        ]
        cursor.executemany(
            "INSERT INTO GymLocations (LocationName, Address, EmailAddress, ContactNumber, Description) VALUES (?,?,?,?,?)",
            locations
        )

    cursor.execute("SELECT COUNT(*) FROM GymFeatures")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT LocationID FROM GymLocations LIMIT 1")
        loc_row = cursor.fetchone()
        if loc_row:
            loc_id = loc_row[0]
            features = [
                (loc_id, "Olympic Swimming Pool", "50-metre competition-standard swimming pool with lane dividers.", ""),
                (loc_id, "Free Weights Area", "Extensive free weights section with dumbbells up to 60kg.", ""),
                (loc_id, "Cardio Zone", "100+ cardio machines including treadmills, bikes, and rowers.", ""),
                (loc_id, "Group Exercise Studios", "Three dedicated studios for fitness classes.", ""),
                (loc_id, "Sauna & Steam Room", "Luxury sauna and steam room for post-workout recovery.", ""),
                (loc_id, "Nutrition Bar", "On-site nutrition bar with protein shakes and healthy snacks.", ""),
            ]
            cursor.executemany(
                "INSERT INTO GymFeatures (LocationID, FeatureName, FeatureDescription, ImagePath) VALUES (?,?,?,?)",
                features
            )

    cursor.execute("SELECT COUNT(*) FROM GymStaff")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT LocationID FROM GymLocations LIMIT 1")
        loc_row = cursor.fetchone()
        if loc_row:
            loc_id = loc_row[0]
            staff = [
                (loc_id, "James", "Wilson", "Head Personal Trainer", "James has 15 years of experience in strength and conditioning. He specialises in powerlifting and functional fitness.", ""),
                (loc_id, "Sarah", "Thompson", "Yoga & Pilates Instructor", "Sarah is a certified yoga and pilates instructor with a passion for mindfulness and flexibility training.", ""),
                (loc_id, "Marcus", "Brown", "Cardio & HIIT Coach", "Marcus is an ex-professional footballer who now coaches high-intensity interval training and cardio fitness.", ""),
                (loc_id, "Emma", "Davis", "Nutrition Coach", "Emma holds a degree in Sports Nutrition and helps members achieve their dietary goals alongside their fitness routines.", ""),
                (loc_id, "Tom", "Anderson", "Swimming Coach", "Tom is a former competitive swimmer who coaches all ability levels from beginners to advanced.", ""),
            ]
            cursor.executemany(
                "INSERT INTO GymStaff (LocationID, FirstName, LastName, Role, Bio, ImagePath) VALUES (?,?,?,?,?,?)",
                staff
            )

    cursor.execute("SELECT COUNT(*) FROM MembershipDurations")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT LocationID FROM GymLocations")
        loc_ids = [row[0] for row in cursor.fetchall()]
        for loc_id in loc_ids:
            durations = [
                (loc_id, "1 Month", 30),
                (loc_id, "3 Months", 90),
                (loc_id, "6 Months", 180),
                (loc_id, "12 Months", 365),
            ]
            cursor.executemany(
                "INSERT INTO MembershipDurations (LocationID, DurationName, NumberOfDays) VALUES (?,?,?)",
                durations
            )

    cursor.execute("SELECT COUNT(*) FROM MembershipPackages")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT LocationID FROM GymLocations")
        loc_ids = [row[0] for row in cursor.fetchall()]
        for loc_id in loc_ids:
            packages = [
                (loc_id, "Basic", "Access to gym floor, changing rooms, and lockers. Great for those who prefer to train independently."),
                (loc_id, "Standard", "All Basic features plus unlimited fitness classes and access to all studios."),
                (loc_id, "Premium", "All Standard features plus personal training sessions (2 per month), nutrition consultations, and premium locker."),
            ]
            cursor.executemany(
                "INSERT INTO MembershipPackages (LocationID, PackageName, Description) VALUES (?,?,?)",
                packages
            )

    cursor.execute("SELECT COUNT(*) FROM MembershipPrices")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT PackageID, LocationID FROM MembershipPackages")
        packages = cursor.fetchall()
        for pkg_id, loc_id in packages:
            cursor.execute("SELECT DurationID, NumberOfDays FROM MembershipDurations WHERE LocationID = ?", (loc_id,))
            durations = cursor.fetchall()
            cursor.execute("SELECT PackageName FROM MembershipPackages WHERE PackageID = ?", (pkg_id,))
            pkg_name = cursor.fetchone()[0]

            base_prices = {"Basic": 30, "Standard": 50, "Premium": 80}
            base = base_prices.get(pkg_name, 30)
            for dur_id, num_days in durations:
                multiplier = num_days / 30
                discount = 0.9 if num_days >= 90 else (0.85 if num_days >= 180 else 0.8) if num_days >= 365 else 1.0
                price = round(base * multiplier * discount, 2)
                cursor.execute(
                    "INSERT INTO MembershipPrices (PackageID, DurationID, Price) VALUES (?,?,?)",
                    (pkg_id, dur_id, price)
                )

    cursor.execute("SELECT COUNT(*) FROM MembershipPackagesFeatures")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT PackageID, PackageName FROM MembershipPackages")
        packages = cursor.fetchall()
        all_features = [
            "Gym Floor Access", "Changing Rooms", "Locker Access",
            "Unlimited Classes", "Studio Access", "Swimming Pool",
            "Personal Training", "Nutrition Consultation", "Premium Locker"
        ]
        feature_inclusion = {
            "Basic": [True, True, True, False, False, False, False, False, False],
            "Standard": [True, True, True, True, True, True, False, False, False],
            "Premium": [True, True, True, True, True, True, True, True, True],
        }
        for pkg_id, pkg_name in packages:
            inclusions = feature_inclusion.get(pkg_name, [False] * len(all_features))
            for feature, included in zip(all_features, inclusions):
                cursor.execute(
                    "INSERT INTO MembershipPackagesFeatures (PackageID, FeatureName, IsIncluded) VALUES (?,?,?)",
                    (pkg_id, feature, included)
                )

    cursor.execute("SELECT COUNT(*) FROM MemberDailyPrices")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT LocationID FROM GymLocations")
        loc_ids = [row[0] for row in cursor.fetchall()]
        for loc_id in loc_ids:
            daily_prices = [
                (loc_id, 1, 1, 10.00),
                (loc_id, 2, 3, 8.50),
                (loc_id, 3, 7, 7.00),
            ]
            cursor.executemany(
                "INSERT INTO MemberDailyPrices (LocationID, NumberOfDaysID, NumberOfDays, DailyPrice) VALUES (?,?,?,?)",
                daily_prices
            )

    cursor.execute("SELECT COUNT(*) FROM GymClasses")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT LocationID FROM GymLocations LIMIT 1")
        loc_row = cursor.fetchone()
        if loc_row:
            loc_id = loc_row[0]
            cursor.execute("SELECT StaffID FROM GymStaff WHERE LocationID = ? LIMIT 3", (loc_id,))
            staff_ids = [row[0] for row in cursor.fetchall()]
            instructor_id = staff_ids[0] if staff_ids else None

            classes = [
                (loc_id, "Morning Yoga", "A relaxing morning yoga session to start your day.", instructor_id, 20, "Beginner", "Yoga"),
                (loc_id, "HIIT Blast", "High-intensity interval training for maximum calorie burn.", instructor_id, 25, "Advanced", "HIIT"),
                (loc_id, "Spin Class", "High energy indoor cycling class.", instructor_id, 30, "Intermediate", "Cardio"),
                (loc_id, "Pilates Core", "Core-focused pilates to strengthen and tone.", instructor_id, 20, "Beginner", "Pilates"),
                (loc_id, "BoxFit", "Boxing-inspired fitness workout combining cardio and strength.", instructor_id, 25, "Intermediate", "Cardio"),
                (loc_id, "Aqua Aerobics", "Low-impact water-based aerobics class.", instructor_id, 30, "Beginner", "Swimming"),
            ]
            cursor.executemany(
                "INSERT INTO GymClasses (LocationID, ClassName, ClassDescription, InstructorID, MaxCapacity, DifficultyLevel, ClassType) VALUES (?,?,?,?,?,?,?)",
                classes
            )

    cursor.execute("SELECT COUNT(*) FROM ClassSchedule")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT ClassID FROM GymClasses LIMIT 6")
        class_ids = [row[0] for row in cursor.fetchall()]
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        times = ["07:00", "09:00", "12:00", "14:00", "17:00", "19:00"]
        for i, class_id in enumerate(class_ids):
            for j, day in enumerate(days[:3]):
                schedule = (class_id, day, times[i % len(times)], "01:00", f"Studio {i + 1}")
                cursor.execute(
                    "INSERT INTO ClassSchedule (ClassID, DayOfWeek, StartTime, Duration, RoomNumber) VALUES (?,?,?,?,?)",
                    schedule
                )

    cursor.execute("SELECT COUNT(*) FROM Meals")
    if cursor.fetchone()[0] == 0:
        meals = [
            ("Avocado Toast", "Breakfast", "A nutritious breakfast with whole grain toast and fresh avocado.", 320, 12, 18, 35, "Avocado,Whole Grain Bread,Lemon,Salt,Pepper", 10, "", "", "General Fitness", 5.50, "Vegetarian", "Gluten", 1),
            ("Grilled Chicken Salad", "Lunch", "A healthy and filling chicken salad with mixed greens.", 380, 35, 12, 18, "Chicken Breast,Mixed Greens,Tomatoes,Cucumber,Olive Oil", 20, "", "", "Weight Loss", 8.00, "None", "None", 1),
            ("Salmon with Quinoa", "Dinner", "Omega-3 rich salmon paired with protein-packed quinoa.", 520, 45, 22, 40, "Salmon Fillet,Quinoa,Lemon,Dill,Olive Oil", 30, "", "", "Muscle Gain", 12.00, "None", "Fish", 1),
            ("Greek Yogurt Bowl", "Breakfast", "Protein-rich yogurt with berries and granola.", 280, 18, 8, 38, "Greek Yogurt,Mixed Berries,Granola,Honey", 5, "", "", "General Fitness", 4.00, "Vegetarian", "Dairy,Gluten", 1),
            ("Black Bean Tacos", "Lunch", "Flavourful plant-based tacos with black beans.", 420, 16, 14, 58, "Black Beans,Corn Tortillas,Salsa,Avocado,Lime", 15, "", "", "Weight Loss", 6.50, "Vegan", "None", 2),
            ("Turkey & Sweet Potato", "Dinner", "Lean turkey mince with roasted sweet potato.", 480, 38, 10, 55, "Turkey Mince,Sweet Potato,Broccoli,Garlic,Olive Oil", 35, "", "", "Muscle Gain", 9.50, "None", "None", 1),
            ("Protein Smoothie", "Breakfast", "High-protein smoothie to kickstart the day.", 350, 28, 8, 40, "Banana,Protein Powder,Almond Milk,Peanut Butter,Oats", 5, "", "", "Muscle Gain", 3.50, "Vegan", "Nuts,Dairy", 1),
            ("Tuna Nicoise Salad", "Lunch", "Classic French salad with tuna and eggs.", 440, 36, 20, 22, "Tuna,Eggs,Green Beans,Olives,Cherry Tomatoes", 15, "", "", "Weight Loss", 10.00, "None", "Fish,Eggs", 1),
            ("Beef Stir Fry", "Dinner", "Quick and nutritious beef and vegetable stir fry.", 510, 40, 18, 45, "Beef Strips,Broccoli,Peppers,Soy Sauce,Ginger,Brown Rice", 20, "", "", "Muscle Gain", 11.00, "None", "Soy", 1),
            ("Overnight Oats", "Breakfast", "Filling and nutritious overnight oats.", 360, 14, 10, 52, "Oats,Almond Milk,Chia Seeds,Banana,Honey", 5, "", "", "General Fitness", 3.00, "Vegan", "Gluten", 1),
        ]
        cursor.executemany(
            "INSERT INTO Meals (MealName, MealType, MealSummary, Calories, Protein, Fat, Carbohydrates, Ingredients, CookingTime, ImagePath, PdfPath, NutritionalGoals, Budget, DietaryRestrictions, Allergies, MealSize) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            meals
        )

    cursor.execute("SELECT COUNT(*) FROM Workouts")
    if cursor.fetchone()[0] == 0:
        workouts = [
            ("Full Body Strength", "Strength", "Muscle Gain", "A comprehensive full body strength training workout.", "Intermediate", "", "Dumbbells,Barbell", 10, 10),
            ("Morning Cardio Run", "Cardio", "Weight Loss", "A steady-state cardio run to burn calories and improve endurance.", "Beginner", "", "None", 5, 10),
            ("HIIT Circuit", "HIIT", "Weight Loss", "A high-intensity circuit training session for maximum fat burn.", "Advanced", "", "Resistance Bands,Dumbbells", 5, 15),
            ("Yoga Flow", "Flexibility", "Flexibility", "A gentle yoga flow to improve flexibility and reduce stress.", "Beginner", "", "Yoga Mat", 10, 15),
            ("Swimming Endurance", "Swimming", "Endurance", "Endurance swimming workout to build stamina.", "Intermediate", "", "Swimsuit", 10, 10),
            ("Upper Body Power", "Strength", "Muscle Gain", "Focus on building upper body strength and definition.", "Advanced", "", "Barbell,Dumbbells", 10, 10),
            ("Pilates Core", "Flexibility", "General Fitness", "Core-strengthening pilates routine.", "Beginner", "", "Yoga Mat", 5, 10),
            ("Interval Run", "Cardio", "Endurance", "Alternating high and low intensity running intervals.", "Intermediate", "", "None", 5, 10),
        ]
        cursor.executemany(
            "INSERT INTO Workouts (WorkoutName, WorkoutType, WorkoutGoal, Description, Difficulty, ImagePath, Equipment, WarmupDuration, CooldownDuration) VALUES (?,?,?,?,?,?,?,?,?)",
            workouts
        )

    cursor.execute("SELECT COUNT(*) FROM Exercises")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT WorkoutID, WorkoutName FROM Workouts")
        workouts = cursor.fetchall()

        exercise_templates = {
            "Full Body Strength": [
                ("Barbell Squat", 4, 8, 0, "Compound leg exercise for building overall strength."),
                ("Bench Press", 3, 10, 0, "Chest and tricep pressing movement."),
                ("Deadlift", 3, 6, 0, "Full body posterior chain exercise."),
                ("Pull-ups", 3, 8, 0, "Back and bicep pulling movement."),
                ("Overhead Press", 3, 10, 0, "Shoulder pressing exercise."),
            ],
            "Morning Cardio Run": [
                ("Warm-up Walk", 1, 1, 300, "5-minute brisk walk to warm up."),
                ("Steady Jog", 1, 1, 1800, "30-minute steady-pace run."),
                ("Cool-down Walk", 1, 1, 300, "5-minute cool-down walk."),
            ],
            "HIIT Circuit": [
                ("Burpees", 4, 10, 0, "Full body explosive movement."),
                ("Box Jumps", 4, 8, 0, "Plyometric leg power exercise."),
                ("Mountain Climbers", 4, 20, 0, "Core and cardio combination."),
                ("Kettlebell Swings", 4, 15, 0, "Hip hinge power movement."),
            ],
            "Yoga Flow": [
                ("Downward Dog", 3, 1, 30, "Core yoga pose for flexibility."),
                ("Warrior I", 3, 1, 30, "Standing balance and strength."),
                ("Child's Pose", 2, 1, 60, "Restorative resting pose."),
                ("Cat-Cow Stretch", 1, 10, 0, "Spinal mobility exercise."),
            ],
        }

        for workout_id, workout_name in workouts:
            exercises = exercise_templates.get(workout_name, [
                ("Exercise 1", 3, 10, 0, "Fundamental exercise for this workout."),
                ("Exercise 2", 3, 12, 0, "Supporting exercise for overall fitness."),
                ("Exercise 3", 3, 10, 0, "Accessory movement to complement the workout."),
            ])
            for ex_name, sets, reps, duration, desc in exercises:
                cursor.execute(
                    "INSERT INTO Exercises (WorkoutID, ExerciseName, Sets, Reps, DurationSeconds, Description) VALUES (?,?,?,?,?,?)",
                    (workout_id, ex_name, sets, reps, duration, desc)
                )

    cursor.execute("SELECT COUNT(*) FROM Testimonials")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT MemberID FROM Members LIMIT 3")
        member_rows = cursor.fetchall()
        if member_rows:
            import datetime
            today = datetime.date.today()
            testimonial_texts = [
                "FitZone completely changed my life! The trainers are amazing and the facilities are world-class. I've lost 15kg in just 4 months!",
                "I was nervous about joining a gym but FitZone made me feel welcome from day one. The classes are brilliant and so much fun!",
                "The personalised workout and meal plans are absolutely brilliant. I've finally found a gym that actually cares about my results.",
            ]
            colors = [("#FFFFFF", "#000000", "#333333"), ("#F0FFF0", "#006400", "#333333"), ("#FFF0F0", "#8B0000", "#333333")]
            for (member_id,), text, (fc, nc, tc) in zip(member_rows, testimonial_texts, colors):
                cursor.execute(
                    "INSERT INTO Testimonials (MemberID, TestimonialText, FrameColor, NameColor, TestimonialColor, TestimonialDate) VALUES (?,?,?,?,?,?)",
                    (member_id, text, fc, nc, tc, today)
                )

    conn.commit()
    conn.close()

    _create_csv_files()
    print("Sample data setup complete.")


def _create_csv_files():
    meals_data = [
        ["MealName", "MealType", "Calories", "Protein", "Fat", "Carbohydrates", "Ingredients", "CookingTime", "NutritionalGoals", "Budget", "DietaryRestrictions", "Allergies", "MealSize"],
        ["Avocado Toast", "Breakfast", "320", "12", "18", "35", "Avocado,Whole Grain Bread,Lemon,Salt,Pepper", "10", "General Fitness", "5.50", "Vegetarian", "Gluten", "1"],
        ["Grilled Chicken Salad", "Lunch", "380", "35", "12", "18", "Chicken Breast,Mixed Greens,Tomatoes,Cucumber,Olive Oil", "20", "Weight Loss", "8.00", "None", "None", "1"],
        ["Salmon with Quinoa", "Dinner", "520", "45", "22", "40", "Salmon Fillet,Quinoa,Lemon,Dill,Olive Oil", "30", "Muscle Gain", "12.00", "None", "Fish", "1"],
    ]

    workouts_data = [
        ["WorkoutName", "WorkoutType", "WorkoutGoal", "Difficulty", "Equipment", "WarmupDuration", "CooldownDuration"],
        ["Full Body Strength", "Strength", "Muscle Gain", "Intermediate", "Dumbbells,Barbell", "10", "10"],
        ["Morning Cardio Run", "Cardio", "Weight Loss", "Beginner", "None", "5", "10"],
        ["HIIT Circuit", "HIIT", "Weight Loss", "Advanced", "Resistance Bands,Dumbbells", "5", "15"],
    ]

    exercises_data = [
        ["WorkoutName", "ExerciseName", "Sets", "Reps", "DurationSeconds", "Description"],
        ["Full Body Strength", "Barbell Squat", "4", "8", "0", "Compound leg exercise."],
        ["Full Body Strength", "Bench Press", "3", "10", "0", "Chest and tricep press."],
        ["Morning Cardio Run", "Steady Jog", "1", "1", "1800", "30-minute steady run."],
    ]

    csv_files = [
        ("meals_data.csv", meals_data),
        ("workouts_data.csv", workouts_data),
        ("exercises_data.csv", exercises_data),
    ]

    for filename, data in csv_files:
        if not os.path.exists(filename):
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(data)


if __name__ == "__main__":
    from gym_setup_database import setup_database
    setup_database()
    setup_sample_data()
