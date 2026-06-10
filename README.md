
## FitZone — SQL Gym Membership Project

FitZone is a small gym‑management system I built to simplify handling memberships, logins, attendance tracking, and basic analytics. The desktop app is built in Python using Tkinter for the interface, Pillow for images, TkCalendar for date inputs, and bcrypt for secure password storage. For data processing, it uses Pandas and NumPy, and it generates simple charts with Matplotlib and SciPy to show patterns such as attendance trends.

Most of the work focused on planning features, designing the interface, structuring the database, and testing each component during development. Adding proper validation and secure login improved reliability, while the analytics features provide clearer insight into how the gym is being used. Overall, FitZone shows how a small tool can streamline daily admin tasks and offer meaningful visibility into member activity.

## How to Run the Code

1. Go to Code → Download ZIP  
2. Extract all files  
3. Open Terminal  
4. Install the required Python packages:

```bash
python -m pip install --upgrade pip
python -m pip install pillow
python -m pip install tkcalendar
python -m pip install bcrypt
python -m pip install matplotlib
python -m pip install scipy
python -m pip install numpy
python -m pip install pandas
python -m pip install captcha
```

5. Run the application:

```bash
python gym_run_page.py
```
