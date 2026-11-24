import sqlite3


def setup_database():
    conn = sqlite3.connect("FitZone.db")
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS GymLocations (
            LocationID INTEGER PRIMARY KEY AUTOINCREMENT,
            LocationName VARCHAR(100) NOT NULL,
            Address VARCHAR(255) NOT NULL,
            EmailAddress VARCHAR(100),
            ContactNumber VARCHAR(20),
            Description TEXT,
            ImagePath VARCHAR(255)
        );

        CREATE TABLE IF NOT EXISTS GymFeatures (
            FeatureID INTEGER PRIMARY KEY AUTOINCREMENT,
            LocationID INTEGER,
            FeatureName VARCHAR(100),
            FeatureDescription TEXT,
            ImagePath VARCHAR(255),
            FOREIGN KEY (LocationID) REFERENCES GymLocations(LocationID)
        );

        CREATE TABLE IF NOT EXISTS GymStaff (
            StaffID INTEGER PRIMARY KEY AUTOINCREMENT,
            LocationID INTEGER,
            FirstName VARCHAR(50),
            LastName VARCHAR(50),
            Role VARCHAR(100),
            Bio TEXT,
            ImagePath VARCHAR(255),
            FOREIGN KEY (LocationID) REFERENCES GymLocations(LocationID)
        );

        CREATE TABLE IF NOT EXISTS MembershipDurations (
            DurationID INTEGER PRIMARY KEY AUTOINCREMENT,
            LocationID INTEGER,
            DurationName VARCHAR(100),
            NumberOfDays INTEGER,
            FOREIGN KEY (LocationID) REFERENCES GymLocations(LocationID)
        );

        CREATE TABLE IF NOT EXISTS MembershipPackages (
            PackageID INTEGER PRIMARY KEY AUTOINCREMENT,
            LocationID INTEGER,
            PackageName VARCHAR(100),
            Description TEXT,
            FOREIGN KEY (LocationID) REFERENCES GymLocations(LocationID)
        );

        CREATE TABLE IF NOT EXISTS MembershipPrices (
            PriceID INTEGER PRIMARY KEY AUTOINCREMENT,
            PackageID INTEGER,
            DurationID INTEGER,
            Price DECIMAL(10,2),
            FOREIGN KEY (PackageID) REFERENCES MembershipPackages(PackageID),
            FOREIGN KEY (DurationID) REFERENCES MembershipDurations(DurationID)
        );

        CREATE TABLE IF NOT EXISTS MembershipPackagesFeatures (
            FeatureID INTEGER PRIMARY KEY AUTOINCREMENT,
            PackageID INTEGER,
            FeatureName VARCHAR(100),
            IsIncluded BOOLEAN,
            FOREIGN KEY (PackageID) REFERENCES MembershipPackages(PackageID)
        );

        CREATE TABLE IF NOT EXISTS Members (
            MemberID INTEGER PRIMARY KEY AUTOINCREMENT,
            LocationID INTEGER,
            DurationID INTEGER,
            PackageID INTEGER,
            Username VARCHAR(50) UNIQUE NOT NULL,
            Password BLOB NOT NULL,
            Salt BLOB NOT NULL,
            Gender VARCHAR(10),
            Email VARCHAR(100),
            DateOfBirth DATE,
            JoinDate DATE,
            FirstName VARCHAR(50),
            LastName VARCHAR(50),
            Address VARCHAR(255),
            CountryCode VARCHAR(10),
            PhoneNumber VARCHAR(20),
            ImagePath VARCHAR(255),
            EmailNotifications BOOLEAN DEFAULT 1,
            FOREIGN KEY (LocationID) REFERENCES GymLocations(LocationID),
            FOREIGN KEY (DurationID) REFERENCES MembershipDurations(DurationID),
            FOREIGN KEY (PackageID) REFERENCES MembershipPackages(PackageID)
        );

        CREATE TABLE IF NOT EXISTS BMIRecords (
            BMIRecordID INTEGER PRIMARY KEY AUTOINCREMENT,
            MemberID INTEGER,
            Weight DECIMAL(5,2),
            Height DECIMAL(5,2),
            BMI DECIMAL(5,2),
            BMICategory VARCHAR(50),
            DateRecorded DATE,
            MeasurementSystem VARCHAR(10),
            FOREIGN KEY (MemberID) REFERENCES Members(MemberID)
        );

        CREATE TABLE IF NOT EXISTS GymClasses (
            ClassID INTEGER PRIMARY KEY AUTOINCREMENT,
            LocationID INTEGER,
            ClassName VARCHAR(100),
            ClassDescription TEXT,
            InstructorID INTEGER,
            MaxCapacity INTEGER,
            DifficultyLevel VARCHAR(20),
            ClassType VARCHAR(50),
            ImagePath VARCHAR(255),
            FOREIGN KEY (LocationID) REFERENCES GymLocations(LocationID),
            FOREIGN KEY (InstructorID) REFERENCES GymStaff(StaffID)
        );

        CREATE TABLE IF NOT EXISTS ClassSchedule (
            ScheduleID INTEGER PRIMARY KEY AUTOINCREMENT,
            ClassID INTEGER,
            DayOfWeek VARCHAR(10),
            StartTime TIME,
            Duration TIME,
            RoomNumber VARCHAR(20),
            FOREIGN KEY (ClassID) REFERENCES GymClasses(ClassID)
        );

        CREATE TABLE IF NOT EXISTS ClassBookings (
            BookingID INTEGER PRIMARY KEY AUTOINCREMENT,
            MemberID INTEGER,
            ScheduleID INTEGER,
            BookingDate DATE,
            Status VARCHAR(20) DEFAULT 'Active',
            FOREIGN KEY (MemberID) REFERENCES Members(MemberID),
            FOREIGN KEY (ScheduleID) REFERENCES ClassSchedule(ScheduleID)
        );

        CREATE TABLE IF NOT EXISTS Testimonials (
            TestimonialID INTEGER PRIMARY KEY AUTOINCREMENT,
            MemberID INTEGER,
            TestimonialText TEXT,
            ImagePath VARCHAR(255),
            FrameColor VARCHAR(20),
            NameColor VARCHAR(20),
            TestimonialColor VARCHAR(20),
            TestimonialDate DATE,
            FOREIGN KEY (MemberID) REFERENCES Members(MemberID)
        );

        CREATE TABLE IF NOT EXISTS Reviews (
            ReviewID INTEGER PRIMARY KEY AUTOINCREMENT,
            MemberID INTEGER,
            LocationID INTEGER,
            Rating INTEGER,
            ReviewText TEXT,
            ReviewDate DATE,
            FOREIGN KEY (MemberID) REFERENCES Members(MemberID),
            FOREIGN KEY (LocationID) REFERENCES GymLocations(LocationID)
        );

        CREATE TABLE IF NOT EXISTS Meals (
            MealID INTEGER PRIMARY KEY AUTOINCREMENT,
            MealName VARCHAR(100),
            MealType VARCHAR(50),
            MealSummary TEXT,
            Calories INTEGER,
            Protein DECIMAL(5,2),
            Fat DECIMAL(5,2),
            Carbohydrates DECIMAL(5,2),
            Ingredients TEXT,
            CookingTime INTEGER,
            ImagePath VARCHAR(255),
            PdfPath VARCHAR(255),
            NutritionalGoals VARCHAR(100),
            Budget DECIMAL(5,2),
            DietaryRestrictions VARCHAR(100),
            Allergies VARCHAR(100),
            MealSize INTEGER
        );

        CREATE TABLE IF NOT EXISTS CustomMeals (
            CustomMealID INTEGER PRIMARY KEY AUTOINCREMENT,
            MemberID INTEGER,
            MealName VARCHAR(100),
            MealType VARCHAR(50),
            MealSummary TEXT,
            Calories INTEGER,
            Protein DECIMAL(5,2),
            Fat DECIMAL(5,2),
            Carbohydrates DECIMAL(5,2),
            Ingredients TEXT,
            CookingTime INTEGER,
            ImagePath VARCHAR(255),
            PdfPath VARCHAR(255),
            NutritionalGoals VARCHAR(100),
            Budget DECIMAL(5,2),
            DietaryRestrictions VARCHAR(100),
            Allergies VARCHAR(100),
            MealSize INTEGER,
            FOREIGN KEY (MemberID) REFERENCES Members(MemberID)
        );

        CREATE TABLE IF NOT EXISTS MealPlans (
            MealPlanID INTEGER PRIMARY KEY AUTOINCREMENT,
            MemberID INTEGER,
            MealID INTEGER,
            PlanDate DATE,
            MealTime VARCHAR(20),
            FOREIGN KEY (MemberID) REFERENCES Members(MemberID),
            FOREIGN KEY (MealID) REFERENCES Meals(MealID)
        );

        CREATE TABLE IF NOT EXISTS Workouts (
            WorkoutID INTEGER PRIMARY KEY AUTOINCREMENT,
            WorkoutName VARCHAR(100),
            WorkoutType VARCHAR(50),
            WorkoutGoal VARCHAR(100),
            Description TEXT,
            Difficulty VARCHAR(20),
            ImagePath VARCHAR(255),
            Equipment VARCHAR(100),
            WarmupDuration INTEGER,
            CooldownDuration INTEGER
        );

        CREATE TABLE IF NOT EXISTS Exercises (
            ExerciseID INTEGER PRIMARY KEY AUTOINCREMENT,
            WorkoutID INTEGER,
            ExerciseName VARCHAR(100),
            Sets INTEGER,
            Reps INTEGER,
            DurationSeconds INTEGER,
            Description TEXT,
            ImagePath VARCHAR(255),
            FOREIGN KEY (WorkoutID) REFERENCES Workouts(WorkoutID)
        );

        CREATE TABLE IF NOT EXISTS WorkoutPlans (
            WorkoutPlanID INTEGER PRIMARY KEY AUTOINCREMENT,
            MemberID INTEGER,
            WorkoutID INTEGER,
            PlanDate DATE,
            FOREIGN KEY (MemberID) REFERENCES Members(MemberID),
            FOREIGN KEY (WorkoutID) REFERENCES Workouts(WorkoutID)
        );

        CREATE TABLE IF NOT EXISTS MemberDailyPrices (
            DailyPriceID INTEGER PRIMARY KEY AUTOINCREMENT,
            LocationID INTEGER,
            NumberOfDaysID INTEGER,
            DailyPrice DECIMAL(10,2),
            NumberOfDays INTEGER,
            FOREIGN KEY (LocationID) REFERENCES GymLocations(LocationID)
        );
    """)

    conn.commit()
    conn.close()
    print("Database setup complete.")


if __name__ == "__main__":
    setup_database()
