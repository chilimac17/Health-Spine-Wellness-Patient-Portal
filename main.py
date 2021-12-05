from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import config
from datetime import datetime, timedelta

# To start go into CDM
# run these commands
# set FLASK_APP=main.py
# set FLASK_DEBUG=1
# python -m flask run


app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = config.mySQLHost
app.config['MYSQL_USER'] = config.mySQLUser
app.config['MYSQL_PASSWORD'] = config.mySQLpass
app.config['MYSQL_DB'] = config.mySQLdatabase

# Intialize MySQL
mysql = MySQL(app)

# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests

#creating list for calendar
events = [
    {
        'todo' : 'Evaluation with Dr.Chillemi',
        'date' : '2021-12-17',

    },
    {
        'todo' : 'Treatment by Dr.Chillemi',
        'date' : '2021-12-12'
    },
{
        'todo' : 'Treatment by Dr.K',
        'date' : '2021-12-14'
    }


]

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('patient_appointments'))


        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))


# http://localhost:5000/Falsk/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        name = request.form['name'].split()
        phone = request.form['phone']
        dob = request.form['dob']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO Users (username, password, email) VALUES ( %s, %s, %s)', (username, password, email,))
            cursor.execute('INSERT INTO Patient (username, first_name, last_name, dob) VALUES ( %s, %s, %s, %s)', (username, name[0], name[1], dob,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'


    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)





# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():

    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE username = %s', (session['username'],))
        # Fetch one record and return result
        account = cursor.fetchone()
        return render_template('Profile.html', username=account['username'], password=account['password'], email=account['email'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/patientinfo')
def patient_info():
    if 'loggedin' in session:
        # Fetch patient record
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Patient WHERE username = %s', (session['username'],))
        patient = cursor.fetchone()
        # Fetch email
        cursor.execute('SELECT email FROM Users WHERE username = %s', (session['username'],))
        user = cursor.fetchone()
        return render_template('My_info.html', first_name=patient['first_name'], last_name=patient['last_name'], dob=patient['dob'], sex=patient['sex'], pain_level=patient['pain_level'], symptoms=patient['symptoms'], email=user['email'])

    # User is not logged in, redirect to login page
    return redirect(url_for('login'))

@app.route('/editinfo', methods=['GET', 'POST'])
def edit_info():
    if 'loggedin' in session:
        # Fetch patient record
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Patient WHERE username = %s', (session['username'],))
        patient = cursor.fetchone()
        # Fetch email
        cursor.execute('SELECT email FROM Users WHERE username = %s', (session['username'],))
        user = cursor.fetchone()

        # Check if POST requests exist
        if request.method == 'POST' and 'first_name' in request.form and 'last_name' in request.form and 'dob' in request.form and 'sex' in request.form and 'pain_level' in request.form and 'symptoms' in request.form and 'email' in request.form:
            # Create variables for easy access
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            dob = request.form['dob']
            sex = request.form['sex']
            pain_level = request.form['pain_level']
            symptoms = request.form['symptoms']
            email = request.form['email']
            print(request.form)

            # Update user and patient information
            cursor.execute('UPDATE Users SET email = %s WHERE username = %s', (email, session['username'],))
            cursor.execute('UPDATE Patient SET first_name = %s, last_name = %s, dob = %s, sex = %s, pain_level = %s, symptoms = %s', (first_name, last_name, dob, sex, pain_level, symptoms))
            mysql.connection.commit()

            return redirect(url_for('patient_info'))

        return render_template('EditInfo.html', first_name=patient['first_name'], last_name=patient['last_name'], dob=patient['dob'], sex=patient['sex'], pain_level=patient['pain_level'], symptoms=patient['symptoms'], email=user['email'])
    # User is not logged in, redirect to login page
    return redirect(url_for('login'))

@app.route('/patientappointments')
def patient_appointments():
    return render_template('MyAppointments.html',events=events)

@app.route('/staffappointments')
def staff_appointments():
    return render_template('patientappointments.html',events=events)

@app.route('/doctorappointments')
def doctor_appointments():
    return render_template('docappointment.html',events=events)

@app.route('/patientsearch')
def patient_search():
    return render_template('patientSearch.html',events=events)

@app.route('/patientinfoupdate')
def patient_info_update():
    return render_template('Profile.html')

@app.route('/calendar')
def calendar():
    return render_template('Calendar.html',events = events)

@app.route('/')
def homepage():
    return render_template('Homepage.html')

@app.route('/AboutUs')
def aboutUs():
    return render_template('AboutPage.html')

@app.route('/ContactUs')
def contactUs():
    return render_template('ContactUs.html')

@app.route('/services')
def services():
    return render_template('Service.html')

@app.route('/schedule', methods=['GET', 'POST'])
def schedule1():
    # Fetch list of doctors
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT first_name, last_name FROM Doctors')
    doctors = cursor.fetchall()

    # Check if POST requests exist (user-submitted form)
    if request.method == 'POST' and 'first_name' in request.form and 'last_name' in request.form and 'email' in request.form and 'phone' in request.form and 'doctor' in request.form:
        # Save POST requests in session
        session['appointment'] = request.form
        # Redirect to next schedule page
        return redirect(url_for('schedule2'))

    return render_template('Schedule1.html', doctors=doctors)

@app.route('/schedule2',methods=['GET', 'POST'])
def schedule2():
    # Check if POST requests exist (user-submitted form)
    if request.method == 'POST' and 'appointment' in session and 'date' in request.form and 'time' in request.form and 'add_info' in request.form:
        # Update appointments POST requests in session
        session['appointment'].update(request.form)

        # Create variables for easy access
        doctor = session['appointment']['doctor']
        email = session['appointment']['email']
        first_name = session['appointment']['first_name']
        last_name = session['appointment']['last_name']
        phone = session['appointment']['phone']
        date = session['appointment']['date']
        start_time = session['appointment']['time']
        end_time = (datetime.strptime(start_time, '%H:%M') + timedelta(hours=1)).strftime('%H:%M') # Create end time (one hour after start time)
        add_info = session['appointment']['add_info']
        patient = session['username']
        print((date, start_time, end_time, patient, doctor, add_info, phone, email,))

        # Insert appointment into Appointments table
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO Appointments (date, start_time, end_time, patient, doctor, additional_info, phone, email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (date, start_time, end_time, patient, doctor, add_info, phone, email,))
        mysql.connection.commit()

        # Redirect to patient appointments page
        return redirect(url_for('patient_appointments'))

    return render_template('Schedule2.html')

if __name__ == '__main__':
    app.run()