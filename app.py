from flask import Flask, render_template, redirect, url_for, request, flash, session
import mysql.connector
from mysql.connector import Error
import hashlib

app = Flask(__name__)
app.secret_key = "secret_key"

# Database connection details
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': 'sunshine',  # Replace with your MySQL password
    'database': 'eHotelManager'
}

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            connection = mysql.connector.connect(**db_config)
            if connection.is_connected():
                cursor = connection.cursor()

                cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
                existing_user = cursor.fetchone()

                if existing_user:
                    flash('Email is already registered', 'error')
                    return redirect(url_for('register'))

                cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, hashed_password))
                connection.commit()
                flash('Registration successful', 'success')

        except Error as e:
            print(f"Error: {e}")
            flash('An error occurred, please try again.', 'error')
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        return redirect(url_for('login'))

    return render_template('register.html')

# Login route for users
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            connection = mysql.connector.connect(**db_config)
            if connection.is_connected():
                cursor = connection.cursor()

                cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, hashed_password))
                user = cursor.fetchone()

                if user:
                    session['user_id'] = user[0]
                    return redirect(url_for('welcome'))
                else:
                    flash('Invalid login credentials', 'error')

        except Error as e:
            print(f"Error: {e}")
            flash('An error occurred, please try again.', 'error')
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        return redirect(url_for('login'))

    return render_template('login.html')

# Admin Login Route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_email = request.form['email']
        admin_password = request.form['password']
        hashed_password = hashlib.sha256(admin_password.encode()).hexdigest()

        try:
            connection = mysql.connector.connect(**db_config)
            if connection.is_connected():
                cursor = connection.cursor()

                cursor.execute('SELECT * FROM admin WHERE email = %s AND password = %s', (admin_email, hashed_password))
                admin = cursor.fetchone()

                if admin:
                    session['admin_id'] = admin[0]
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Invalid login credentials', 'error')

        except Error as e:
            print(f"Error: {e}")
            flash('An error occurred, please try again.', 'error')
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

# Admin Dashboard route
@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()

            # Fetch number of rooms, room status, and customer information
            cursor.execute('SELECT COUNT(id) FROM rooms')
            num_rooms = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(id) FROM payments WHERE status = "Pending"')
            pending_payments = cursor.fetchone()[0]

            cursor.execute('SELECT username, email FROM users')
            customers = cursor.fetchall()

            cursor.execute('SELECT * FROM complaints')
            complaints = cursor.fetchall()

            # Fetch room data
            cursor.execute('SELECT * FROM rooms')
            rooms = cursor.fetchall()

    except Error as e:
        print(f"Error: {e}")
        flash('An error occurred while fetching the data', 'error')
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template('admin_dashboard.html', num_rooms=num_rooms, pending_payments=pending_payments,
                           customers=customers, complaints=complaints, rooms=rooms)

# Update room status
@app.route('/update_room_status', methods=['POST'])
def update_room_status():
    room_id = request.form['room_id']
    status = request.form['status']

    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()

            cursor.execute('UPDATE rooms SET status = %s WHERE id = %s', (status, room_id))
            connection.commit()
            flash('Room status updated successfully', 'success')

    except Error as e:
        print(f"Error: {e}")
        flash('An error occurred, please try again.', 'error')
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('admin_dashboard'))

# Delete room
@app.route('/delete_room', methods=['POST'])
def delete_room():
    room_id = request.form['room_id']

    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()

            cursor.execute('DELETE FROM rooms WHERE id = %s', (room_id,))
            connection.commit()
            flash('Room deleted successfully', 'success')

    except Error as e:
        print(f"Error: {e}")
        flash('An error occurred, please try again.', 'error')
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('admin_dashboard'))

# Logout route for admin
@app.route('/admin_logout', methods=['GET'])
def admin_logout():
    session.pop('admin_id', None)
    return redirect(url_for('admin_login'))




# Welcome route with features
@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Handle room status update
    if request.method == 'POST' and 'update_status' in request.form:
        room_id = request.form['room_id']
        status = request.form['status']
        
        try:
            connection = mysql.connector.connect(**db_config)
            if connection.is_connected():
                cursor = connection.cursor()

                cursor.execute('UPDATE rooms SET status = %s WHERE id = %s', (status, room_id))
                connection.commit()
                flash('Room status updated successfully', 'success')

        except Error as e:
            print(f"Error: {e}")
            flash('An error occurred, please try again.', 'error')
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    # Handle complaint submission
    if request.method == 'POST' and 'submit_complaint' in request.form:
        complaint_text = request.form['complaint_text']
        
        try:
            connection = mysql.connector.connect(**db_config)
            if connection.is_connected():
                cursor = connection.cursor()

                cursor.execute('INSERT INTO complaints (user_id, complaint_text) VALUES (%s, %s)', (session['user_id'], complaint_text))
                connection.commit()
                flash('Complaint submitted successfully', 'success')

        except Error as e:
            print(f"Error: {e}")
            flash('An error occurred, please try again.', 'error')
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    return render_template('welcome.html')

if __name__ == '__main__':
    app.run(debug=True)
