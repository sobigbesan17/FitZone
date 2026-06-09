import sys
import os
import sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gym_setup_database import setup_database
from gym_setup_sample_data import setup_sample_data
from gym_home_page import GymHomePage
from gym_login import GymLogin
from gym_forgot_password import GymForgotPassword
from gym_account_verification import GymAccountVerification
from gym_set_new_password import GymSetNewPassword
from gym_select_your_gym_page import GymSelectionPage
from gym_membership_duration_registration_page import GymMembershipDurationPage
from gym_membership_package_registration_page import GymMembershipPackagePage
from gym_user_details_registration_page import GymDetailsRegistrationPage
from gym_payment_registration_page import GymPaymentPage
from gym_registration_success_page import GymRegistrationSuccessPage
from gym_fitness_dashboard_page import FitnessDashboardPage
from gym_calculate_bmi_page import CalculateBMIPage
from gym_bmi_visualisation_report_page import BMIVisualisationReportPage
from gym_personalised_meal_planner import PersonalisedMealPlannerPage
from gym_personalised_workout_planner import PersonalisedWorkoutPlannerPage
from gym_booking_class_page import GymClassBookingPage
from gym_class_reservations_page import GymClassReservationPage
from gym_view_member_class_schedule_page import GymMemberClassSchedulePage
from gym_view_member_class_clashes_page import GymClassClashesPage
from gym_modify_classes_page import LeaveClassPage
from gym_user_update_profile_page import GymUpdateProfilePage
from gym_meal_page import GymMealPage
from gym_workouts_page import GymWorkoutsPage
from gym_reviews_page import GymReviewsPage
from gym_features_registration_page import GymFeaturesPage
from gym_view_the_gym_team import GymViewTeamPage


class GymManager:
    def __init__(self):
        self.current_page = None
        self.member_id = None
        self.username = None
        self.location_id = None

        self.forgot_password_email = None
        self.forgot_password_username = None
        self.verification_member_id = None

        self.gym_selection_page = None
        self.membership_duration_page = None
        self.membership_package_page = None
        self.user_details_page = None
        self.payment_page = None
        self.member_image_path = None

        setup_database()
        setup_sample_data()

        self.show_home()

    def _destroy_current(self):
        if self.current_page:
            try:
                self.current_page.destroy()
            except Exception:
                pass
            self.current_page = None

    def _apply_shared_page_callbacks(self, page):
        try:
            page.login_callback = self.show_login
            page.logout_callback = self.logout
            page.signup_callback = self.show_select_gym
            page.update_profile_callback = self.show_update_profile
            page.home_callback = self.show_home
            page.meal_callback = self.show_meals
            page.workout_callback = self.show_workouts
            page.view_gym_team_callback = self.show_gym_team
            page.view_class_schedule_callback = self.show_class_schedule
            page.view_bmi_visualisation_callback = self.show_bmi_visualisation
            page.gym_class_clashes_callback = self.show_class_clashes
            page.member_id = getattr(self, "member_id", None)
            page.location_id = getattr(self, "location_id", None)
            page.username = getattr(self, "username", None)
            page.profile_image_path = getattr(self, "member_image_path", None)
        except Exception:
            pass

    def _display_page(self, page):
        self._apply_shared_page_callbacks(page)
        self.current_page = page
        page.mainloop()

    def show_home(self):
        self._destroy_current()
        page = GymHomePage(
            login_callback=self.show_login,
            select_gym_callback=self.show_select_gym,
            logout_callback=self.logout,
            view_gym_team_callback=self.show_gym_team,
            gym_features_callback=self.show_gym_features,
            reviews_callback=self.show_reviews,
            meal_callback=self.show_meals,
            workout_callback=self.show_workouts,
            home_callback=self.show_home,
            member_id=self.member_id,
            username=self.username,
            location_id=self.location_id,
            view_class_schedule_callback=self.show_class_schedule,
            gym_class_clashes_callback=self.show_class_clashes,
        )
        self._display_page(page)

    def show_login(self):
        self._destroy_current()
        page = GymLogin(
            select_your_gym_callback=self.show_select_gym,
            forgot_password_callback=self.show_forgot_password,
            successful_login_callback=self._on_login_success,
        )
        self._display_page(page)

    def _on_login_success(self):
        if self.current_page:
            self.member_id = self.current_page.get_member_id()
            self.username = getattr(self.current_page, "username", None)
            self.location_id = self.current_page.get_location_id()
        self._load_member_profile_image_path()
        self.show_fitness_dashboard()

    def logout(self):
        self.member_id = None
        self.location_id = None
        self.member_image_path = None
        self.show_home()

    def show_forgot_password(self):
        self._destroy_current()
        page = GymForgotPassword(
            account_verification_callback=self._on_forgot_password_submit,
        )
        self._display_page(page)

    def _on_forgot_password_submit(self):
        if self.current_page:
            self.forgot_password_email = self.current_page.get_email()
            self.forgot_password_username = self.current_page.get_username()
        self.show_account_verification()

    def show_account_verification(self):
        self._destroy_current()
        page = GymAccountVerification(
            email=self.forgot_password_email or "",
            username=self.forgot_password_username or "",
            set_new_password_callback=self._on_verification_success,
        )
        self._display_page(page)

    def _on_verification_success(self):
        if self.current_page:
            self.verification_member_id = self.current_page.get_member_id()
        self.show_set_new_password()

    def show_set_new_password(self):
        self._destroy_current()
        page = GymSetNewPassword(
            member_id=self.verification_member_id,
            login_callback=self.show_login,
        )
        self._display_page(page)

    def show_select_gym(self):
        self._destroy_current()
        page = GymSelectionPage(
            membership_duration_callback=self._on_gym_selected,
        )
        self.gym_selection_page = page
        self._display_page(page)

    def _on_gym_selected(self):
        if self.gym_selection_page:
            self.location_id = self.gym_selection_page.get_location_id()
        self.show_membership_duration()

    def show_membership_duration(self):
        self._destroy_current()
        page = GymMembershipDurationPage(
            location_id=self.location_id,
            membership_package_callback=self._on_duration_selected,
        )
        self.membership_duration_page = page
        self._display_page(page)

    def _on_duration_selected(self):
        self.show_membership_package()

    def show_membership_package(self):
        duration_id = 0
        if self.membership_duration_page:
            duration_id = self.membership_duration_page.get_membership_duration_id() or 0
        self._destroy_current()
        page = GymMembershipPackagePage(
            location_id=self.location_id,
            membership_duration=duration_id,
            user_detail_callback=self._on_package_selected,
            login_callback=self.show_login,
            signup_callback=self.show_select_gym,
        )
        self.membership_package_page = page
        self._display_page(page)

    def _on_package_selected(self):
        self.show_user_details()

    def show_user_details(self):
        self._destroy_current()
        page = GymDetailsRegistrationPage(
            payment_registration_callback=self._on_user_details_submitted,
        )
        self.user_details_page = page
        self._display_page(page)

    def _on_user_details_submitted(self):
        self.show_payment()

    def show_payment(self):
        price = 0.0
        if self.membership_package_page:
            price = self.membership_package_page.get_membership_price() or 0.0
        elif self.membership_duration_page:
            price = self.membership_duration_page.get_membership_price() or 0.0

        self._destroy_current()
        page = GymPaymentPage(
            membership_price=price,
            registration_success_callback=self._on_payment_success,
        )
        self.payment_page = page
        self._display_page(page)

    def _on_payment_success(self):
        user_details = self._compile_user_details()
        self.show_registration_success(user_details)

    def _compile_user_details(self):
        account_details = []
        if self.user_details_page:
            account_details = self.user_details_page.get_user_account_details()

        package_id = None
        duration_id = None
        if self.membership_package_page:
            package_id = self.membership_package_page.get_membership_package_id()
        if self.membership_duration_page:
            duration_id = self.membership_duration_page.get_membership_duration_id()

        if len(account_details) >= 14:
            users_detail = [
                self.location_id,   # LocationID
                duration_id,        # DurationID
                package_id,         # PackageID
            ] + account_details
        else:
            users_detail = [self.location_id, duration_id, package_id] + account_details

        return users_detail

    def show_registration_success(self, users_detail):
        self._destroy_current()
        page = GymRegistrationSuccessPage(
            users_detail=users_detail,
            home_callback=self.show_home,
        )
        self._display_page(page)

    def show_fitness_dashboard(self):
        self._destroy_current()
        page = FitnessDashboardPage(
            member_id=self.member_id,
            fitness_dashboard_callback=self.show_fitness_dashboard,
            calculate_bmi_callback=self.show_calculate_bmi,
            bmi_visualisation_callback=self.show_bmi_visualisation,
            gym_meal_planner_callback=self.show_meal_planner,
            gym_workout_planner_callback=self.show_workout_planner,
            view_class_schedule_callback=self.show_class_schedule,
            gym_class_booking_callback=self.show_class_booking,
            gym_class_clashes_callback=self.show_class_clashes,
        )
        self._display_page(page)

    def show_calculate_bmi(self):
        self._destroy_current()
        page = CalculateBMIPage(
            member_id=self.member_id,
            fitness_dashboard_callback=self.show_fitness_dashboard,
            calculate_bmi_callback=self.show_calculate_bmi,
            bmi_visualisation_callback=self.show_bmi_visualisation,
            gym_meal_planner_callback=self.show_meal_planner,
            gym_workout_planner_callback=self.show_workout_planner,
            view_class_schedule_callback=self.show_class_schedule,
            gym_class_booking_callback=self.show_class_booking,
            gym_class_clashes_callback=self.show_class_clashes,
        )
        self._display_page(page)

    def show_bmi_visualisation(self):
        self._destroy_current()
        page = BMIVisualisationReportPage(
            member_id=self.member_id,
            fitness_dashboard_callback=self.show_fitness_dashboard,
            calculate_bmi_callback=self.show_calculate_bmi,
            bmi_visualisation_callback=self.show_bmi_visualisation,
            gym_meal_planner_callback=self.show_meal_planner,
            gym_workout_planner_callback=self.show_workout_planner,
            view_class_schedule_callback=self.show_class_schedule,
            gym_class_booking_callback=self.show_class_booking,
            gym_class_clashes_callback=self.show_class_clashes,
        )
        self._display_page(page)

    def show_meal_planner(self):
        self._destroy_current()
        page = PersonalisedMealPlannerPage(
            member_id=self.member_id,
            fitness_dashboard_callback=self.show_fitness_dashboard,
            calculate_bmi_callback=self.show_calculate_bmi,
            bmi_visualisation_callback=self.show_bmi_visualisation,
            gym_meal_planner_callback=self.show_meal_planner,
            gym_workout_planner_callback=self.show_workout_planner,
            view_class_schedule_callback=self.show_class_schedule,
            gym_class_booking_callback=self.show_class_booking,
            gym_class_clashes_callback=self.show_class_clashes,
        )
        self._display_page(page)

    def show_workout_planner(self):
        self._destroy_current()
        page = PersonalisedWorkoutPlannerPage(
            member_id=self.member_id,
            fitness_dashboard_callback=self.show_fitness_dashboard,
            calculate_bmi_callback=self.show_calculate_bmi,
            bmi_visualisation_callback=self.show_bmi_visualisation,
            gym_meal_planner_callback=self.show_meal_planner,
            gym_workout_planner_callback=self.show_workout_planner,
            view_class_schedule_callback=self.show_class_schedule,
            gym_class_booking_callback=self.show_class_booking,
            gym_class_clashes_callback=self.show_class_clashes,
        )
        self._display_page(page)

    def show_class_booking(self):
        self._destroy_current()
        page = GymClassBookingPage(
            member_id=self.member_id,
            location_id=self.location_id,
            fitness_dashboard_callback=self.show_fitness_dashboard,
            calculate_bmi_callback=self.show_calculate_bmi,
            bmi_visualisation_callback=self.show_bmi_visualisation,
            gym_meal_planner_callback=self.show_meal_planner,
            gym_workout_planner_callback=self.show_workout_planner,
            view_class_schedule_callback=self.show_class_schedule,
            gym_class_booking_callback=self.show_class_booking,
            gym_class_clashes_callback=self.show_class_clashes,
        )
        self._display_page(page)

    def show_class_reservations(self):
        self._destroy_current()
        page = GymClassReservationPage(
            member_id=self.member_id,
            location_id=self.location_id,
            fitness_dashboard_callback=self.show_fitness_dashboard,
            calculate_bmi_callback=self.show_calculate_bmi,
            bmi_visualisation_callback=self.show_bmi_visualisation,
            gym_meal_planner_callback=self.show_meal_planner,
            gym_workout_planner_callback=self.show_workout_planner,
            view_class_schedule_callback=self.show_class_schedule,
            gym_class_booking_callback=self.show_class_booking,
            gym_class_clashes_callback=self.show_class_clashes,
        )
        self._display_page(page)

    def show_class_schedule(self):
        self._destroy_current()
        page = GymMemberClassSchedulePage(
            member_id=self.member_id,
            location_id=self.location_id,
            fitness_dashboard_callback=self.show_fitness_dashboard,
            calculate_bmi_callback=self.show_calculate_bmi,
            bmi_visualisation_callback=self.show_bmi_visualisation,
            gym_meal_planner_callback=self.show_meal_planner,
            gym_workout_planner_callback=self.show_workout_planner,
            view_class_schedule_callback=self.show_class_schedule,
            gym_class_booking_callback=self.show_class_booking,
            gym_class_clashes_callback=self.show_class_clashes,
        )
        self._display_page(page)

    def show_class_clashes(self):
        self._destroy_current()
        page = GymClassClashesPage(
            member_id=self.member_id,
            location_id=self.location_id,
            fitness_dashboard_callback=self.show_fitness_dashboard,
            calculate_bmi_callback=self.show_calculate_bmi,
            bmi_visualisation_callback=self.show_bmi_visualisation,
            gym_meal_planner_callback=self.show_meal_planner,
            gym_workout_planner_callback=self.show_workout_planner,
            view_class_schedule_callback=self.show_class_schedule,
            gym_class_booking_callback=self.show_class_booking,
            gym_class_clashes_callback=self.show_class_clashes,
        )
        self._display_page(page)

    def show_leave_class(self):
        self._destroy_current()
        page = LeaveClassPage(
            member_id=self.member_id,
            location_id=self.location_id,
            fitness_dashboard_callback=self.show_fitness_dashboard,
            calculate_bmi_callback=self.show_calculate_bmi,
            bmi_visualisation_callback=self.show_bmi_visualisation,
            gym_meal_planner_callback=self.show_meal_planner,
            gym_workout_planner_callback=self.show_workout_planner,
            view_class_schedule_callback=self.show_class_schedule,
            gym_class_booking_callback=self.show_class_booking,
            gym_class_clashes_callback=self.show_class_clashes,
        )
        self._display_page(page)

    def show_update_profile(self):
        self._destroy_current()
        page = GymUpdateProfilePage(
            member_id=self.member_id,
            home_callback=self.show_home,
            profile_updated_callback=self._on_profile_updated,
        )
        self._display_page(page)

    def show_meals(self):
        self._destroy_current()
        page = GymMealPage(
            member_id=self.member_id,
            location_id=self.location_id,
            home_callback=self.show_home,
            dashboard_callback=self.show_fitness_dashboard if self.member_id else None,
        )
        self._display_page(page)

    def show_workouts(self):
        self._destroy_current()
        page = GymWorkoutsPage(
            member_id=self.member_id,
            location_id=self.location_id,
            home_callback=self.show_home,
            dashboard_callback=self.show_fitness_dashboard if self.member_id else None,
        )
        self._display_page(page)

    def show_reviews(self):
        self._destroy_current()
        page = GymReviewsPage(
            member_id=self.member_id,
            location_id=self.location_id or 1,
            home_callback=self.show_home,
        )
        self._display_page(page)

    def show_gym_features(self):
        self._destroy_current()
        page = GymFeaturesPage(
            location_id=self.location_id or 1,
            home_callback=self.show_home,
        )
        self._display_page(page)

    def show_gym_team(self):
        self._destroy_current()
        page = GymViewTeamPage(
            location_id=self.location_id or 1,
            home_callback=self.show_home,
        )
        self._display_page(page)

    def _on_profile_updated(self, image_path):
        self.member_image_path = image_path or self.member_image_path
        if self.current_page:
            self.current_page.profile_image_path = self.member_image_path
            try:
                self.current_page.refresh_header()
            except Exception:
                pass

    def _load_member_profile_image_path(self):
        try:
            conn = sqlite3.connect("FitZone.db")
            cursor = conn.cursor()
            cursor.execute("SELECT ImagePath FROM Members WHERE MemberID = ?", (self.member_id,))
            result = cursor.fetchone()
            self.member_image_path = result[0] if result and result[0] else None
        except sqlite3.Error:
            self.member_image_path = None
        finally:
            try:
                conn.close()
            except Exception:
                pass


if __name__ == "__main__":
    app = GymManager()
