from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
import sqlite3
import pandas as pd
import secrets
import io
from flask import session

app = Flask(__name__)
app.secret_key = secrets.token_hex(24)

correct_username = "vghadmin"
correct_password = "112507"

# Admin login route
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if entered credentials are correct
        if username == correct_username and password == correct_password:
            session['admin_logged_in'] = True  # Store login status in session
            return redirect(url_for("admin_dashboard"))
        else:
            Flask("Invalid credentials. Please try again.")  # Show error message if credentials are incorrect
            return render_template("admin_login.html")

    return render_template("admin_login.html")

# Admin login route
@app.route("/admin_logout", methods=["GET", "POST"])
def admin_logout():
    session.pop('admin_logged_in', None)
    Flask("You have been logged out.")
    return redirect(url_for('admin_login'))

# Route for homepage (for first-timers and regular check-in)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "first_timer" in request.form:
            return redirect(url_for("first_timer"))
        elif "regular_attendee" in request.form:
            return redirect(url_for("regular_attendee"))
    return render_template("index.html")

# Route for first-timers
@app.route("/first_timer", methods=["GET", "POST"])
def first_timer():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        phone_number = request.form.get("phone_number")
        birthday = request.form.get("birthday")
        is_leader = request.form.get("is_victory_group_leader") == "yes"
        group_leader_name = request.form.get("group_leader_name")
        attending_greenhills = request.form.get("attending_greenhills") == "yes"

        # Set service_time to None if not attending Victory Greenhills
        service_time = request.form.get("service_time") if attending_greenhills else ""

        conn = sqlite3.connect('checkin.db')
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO attendees (first_name, last_name, phone_number, birthday,
                                               is_victory_group_leader, group_leader_name, attending_greenhills, service_time)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                       (first_name, last_name, phone_number, birthday, is_leader, group_leader_name, attending_greenhills, service_time))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("first_timer.html")

# Route for regular attendees (lookup by name)
@app.route("/regular_attendee", methods=["GET", "POST"])
def regular_attendee():
    if request.method == "POST":
        attendee_id = request.form.get("attendee_id")
        conn = sqlite3.connect('checkin.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO attendance_logs (attendee_id) VALUES (?)", (attendee_id,))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    conn = sqlite3.connect('checkin.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, first_name, last_name FROM attendees")
    attendees = cursor.fetchall()
    conn.close()
    return render_template("regular_attendee.html", attendees=attendees)

# Route to search attendees by name
@app.route('/search_attendees')
def search_attendees():
    name_query = request.args.get('name')
    conn = sqlite3.connect('checkin.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, first_name, last_name FROM attendees WHERE first_name LIKE ? OR last_name LIKE ?",
                   ('%' + name_query + '%', '%' + name_query + '%'))
    attendees = cursor.fetchall()
    conn.close()

    return jsonify([{"id": attendee[0], "first_name": attendee[1], "last_name": attendee[2]} for attendee in attendees])

# Admin dashboard route (only accessible if logged in)
@app.route("/admin_dashboard")
def admin_dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))  # Redirect to login if not logged in

    # Fetch and display data for the admin dashboard
    conn = sqlite3.connect('checkin.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendees")
    attendees = cursor.fetchall()
    conn.close()

    return render_template("admin_dashboard.html", attendees=attendees)

# Route to display the edit form for a specific attendee
@app.route("/admin_dashboard/edit_attendee/<int:attendee_id>", methods=["GET", "POST"])
def edit_attendee(attendee_id):
    if request.method == "POST":
        # Get form data
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        phone_number = request.form.get("phone_number")
        birthday = request.form.get("birthday")
        is_leader = request.form.get("is_victory_group_leader") == "yes"
        group_leader_name = request.form.get("group_leader_name")
        attending_greenhills = request.form.get("attending_greenhills") == "yes"
        service_time = request.form.get("service_time")

        conn = sqlite3.connect('checkin.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE attendees
            SET first_name = ?, last_name = ?, phone_number = ?, birthday = ?,
                is_victory_group_leader = ?, group_leader_name = ?,
                attending_greenhills = ?, service_time = ?
            WHERE id = ?
        """, (first_name, last_name, phone_number, birthday, is_leader, group_leader_name, attending_greenhills, service_time, attendee_id))
        conn.commit()
        conn.close()
        return redirect(url_for("admin_dashboard"))

    conn = sqlite3.connect('checkin.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendees WHERE id = ?", (attendee_id,))
    attendee = cursor.fetchone()
    conn.close()

    # Ensure the birthday is in the correct format
    formatted_birthday = attendee[4]  # assuming the birthday is in YYYY-MM-DD format

    return render_template("edit_attendee.html", attendee=attendee, formatted_birthday=formatted_birthday)

@app.route("/admin_dashboard/delete_attendee/<int:attendee_id>", methods=["GET"])
def delete_attendee(attendee_id):
    conn = sqlite3.connect('checkin.db')
    cursor = conn.cursor()

    # Delete attendee from the database
    cursor.execute("DELETE FROM attendees WHERE id = ?", (attendee_id,))
    conn.commit()
    conn.close()

    # Redirect back to the admin dashboard after deletion
    return redirect(url_for("admin_dashboard"))


# Route to download the database as an Excel file
@app.route("/admin_dashboard/download", methods=["GET"])
def download_database():
    conn = sqlite3.connect('checkin.db')
    df = pd.read_sql_query("SELECT * FROM attendees", conn)

    buffer = io.BytesIO()
    df.to_excel(buffer)
    headers = {
        'Content-Disposition': 'attachment; filename=output.xlsx',
        'Content-type': 'application/vnd.ms-excel'
    }
    conn.close()
    return Response(buffer.getvalue(), mimetype='application/vnd.ms-excel', headers=headers)

@app.route("/admin_dashboard/report", methods=["GET"])
def attendance_report():
    conn = sqlite3.connect('checkin.db')
    cursor = conn.cursor()

    # Weekly Attendance (last 7 days) filtered by multiple dates if provided
    selected_dates = request.args.getlist('dates')
    date_condition = "WHERE visit_date IN (" + ", ".join(f"'{date}'" for date in selected_dates) + ")" if selected_dates else "WHERE visit_date >= date('now', '-7 days')"

    cursor.execute(f"SELECT visit_date, COUNT(*) FROM attendance_logs {date_condition} GROUP BY visit_date ORDER BY visit_date DESC")
    weekly_attendance_by_date = cursor.fetchall()

    # Monthly Average Attendance with rounding (no .0)
    cursor.execute("""
        SELECT strftime('%m', visit_date) AS month, ROUND(AVG(attendance_count))
        FROM (
            SELECT visit_date, COUNT(*) AS attendance_count
            FROM attendance_logs
            GROUP BY visit_date
        )
        GROUP BY month
    """)
    monthly_data = cursor.fetchall()

    # Map numeric month to full month names
    months_mapping = {
        '01': 'January',
        '02': 'February',
        '03': 'March',
        '04': 'April',
        '05': 'May',
        '06': 'June',
        '07': 'July',
        '08': 'August',
        '09': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December'
    }
    monthly_data = [(months_mapping[str(month)], int(count)) for month, count in monthly_data]

    # Query to get unique dates for the dropdown
    cursor.execute("SELECT DISTINCT visit_date FROM attendance_logs")
    available_dates = [row[0] for row in cursor.fetchall()]

    conn.close()
    return render_template("report.html", weekly_attendance_by_date=weekly_attendance_by_date, monthly_data=monthly_data, available_dates=available_dates)

if __name__ == "__main__":
    app.run(debug=True)
