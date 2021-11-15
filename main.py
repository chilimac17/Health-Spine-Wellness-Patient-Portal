from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import config

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

#possible dup
@app.route('/patientinfo')
def patient_info():
    return render_template('My_info.html')

@app.route('/patientappointments')
def patient_appointments():
    return render_template('MyAppointments.html')

@app.route('/patientinfoupdate')
def patient_info_update():
    return render_template('Profile.html')

@app.route('/calendar')
def calendar():
    return render_template('calender.html')

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

@app.route('/schedule')
def schedule1():
    return render_template('Schedule1.html')

@app.route('/schedule2')
def schedule2():
    return render_template('Schedule2.html')

if __name__ == '__main__':
    app.run()