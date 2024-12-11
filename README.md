# CS50’s Introduction to Computer Science Final Project 

## Event Check-in and Database System
#### Video Demo: <URL HERE>
#### Description: 
This project is a web application for managing event attendees and their check-ins. It provides features such as admin dashboard, attendee management, and reports.

## Features:
- User authentication for admin access.
- Admin dashboard for viewing and managing attendee data.
- Check-in forms for first-time attendees and regular attendees.
- Reporting of weekly and monthly attendance.

## Usage
1. **Home Page**: Allows attendees to check in and add new attendees to the database.
2. **Attendance Logging**: Each check-in is logged for the admin's attendance report.
3. **Admin Access**: Provides full read and write access to the attendee database.
4. **Reporting**: Admins can view reports and download the database in various formats.

## Technologies Used
- Flask: Web framework for building the application.
- SQLite: Database for managing attendee data and check-ins.
- Jinja2: Template engine for rendering dynamic HTML pages.
- HTML/CSS: For creating and styling the frontend.
- JavaScript: Used for interactive features like attendee search and form validation.
- Bootstrap: Framework for responsive and user-friendly design.

## Project Structure
   ```bash
   project/  
   ├── static/  
   │   └── styles.css            # Contains CSS and other static assets used for styling and enhanced visual presentation of the application.  
   ├── templates/  
   │   ├── admin_dashboard.html  # Admin panel for managing attendees, downloading database as Excel, and viewing reports.  
   │   ├── admin_login.html      # Admin login page for secure access.  
   │   ├── base.html             # Base template including the navigation bar for the entire application.  
   │   ├── edit_attendee.html    # Page for admin to edit attendee details.  
   │   ├── index.html            # Home page for check-in and new attendee addition.  
   │   ├── regular_attendee.html # Page for attendees already in the database to check-in.  
   │   └── report.html           # Displays detailed attendance reports.  
   ├── app.py                    # The main Python file containing the Flask application and routes.
   ├── checkin.db                # The SQLite database used for storing attendee information and event data.
   ├── README.md                 # Documentation for the project.  
   └── requirements.txt          # Lists the dependencies required to run the application.
   ```

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/lloricomichelle/project.git

2. Navigate into the project folder:
   ```bash
   cd project

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   
4. Setup Database:
   - Open a terminal and navigate to the project directory:
     ```bash
     cd project

   - Create the database file:
     ```bash
     sqlite3 checkin.db   

   - Create required tables inside the SQLite shell by executing the following SQL commands:
     ```sql
     CREATE TABLE attendees (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         first_name TEXT NOT NULL,
         last_name TEXT NOT NULL,
         phone_number TEXT,
         birthday TEXT,
         is_victory_group_leader BOOLEAN,
         group_leader_name TEXT,
         attending_greenhills BOOLEAN,
         service_time TEXT
     );
   
     CREATE TABLE sqlite_sequence (name, seq);
      
     CREATE TABLE attendance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attendee_id INTEGER,
        visit_date DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (attendee_id) REFERENCES attendees(id)
     );

   - Exit the SQLite shell:
     ```bash
     .exit

6. Run the application:
   ```bash
   flask run
