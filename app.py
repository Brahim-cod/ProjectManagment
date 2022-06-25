from asyncio import tasks
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_mysqldb import MySQL
import MySQLdb
import re
from flask_socketio import SocketIO

app = Flask(__name__)
app.secret_key = 'qOjLneE5QOa8AEF1GQGhQelVN3452Iwf'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3307
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Ivws3135'
app.config['MYSQL_DB'] = 'project'

socketio = SocketIO(app)
# Intialize MySQL
mysql = MySQL(app)

@app.route('/home')
@app.route('/')
def home():
    if not 'loggedin' in session:
        return redirect(url_for('Login'))
    if session['ischef'] == False:
        return redirect(url_for('userProfile'))
    return render_template('index.html', title = "Dashboard")


@app.route('/chat')
def sessions():
    return render_template('message.html', title="Message")

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

@app.route('/task/update/<int:id>', methods=['GET', 'POST'])
def taskUpdate(id):
    if not 'loggedin' in session:
        return redirect(url_for('Login'))
    if request.method == 'POST' and 'taskName' in request.form and 'taskPriority' in request.form and 'dateStart' in request.form and 'dateFinish' in request.form and 'taskEtat' in request.form and 'taskStatus' in request.form:
        # Create variables for easy access
        name = request.form['taskName']
        finish=request.form['dateFinish']
        start = request.form['dateStart']
        etat=request.form['taskEtat']
        priority = request.form['taskPriority']
        status=request.form['taskStatus']
        if etat == '100':
            status = 'Completed'

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''UPDATE tache
                        SET nomT = %s, dateF = %s, DateD = %s, etat = %s, priority = %s, status = %s
                        WHERE tache_id = %s''', (name, finish, start, etat, priority, status, id, ))
        mysql.connection.commit()
        flash('You have successfully updated task!', "updated")
        return redirect(url_for('userProfile'))
    return redirect(url_for('home'))

@app.route('/task/delete/<int:id>')
def taskDelete(id):
    if not 'loggedin' in session:
        return redirect(url_for('Login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM tache WHERE tache_id = %s', (id,))
    mysql.connection.commit()
    flash('You have successfully deleted task!', "deleted")
    return redirect(url_for('userProfile'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'role' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role=request.form['role']
         # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM EMP WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not role :
            msg='ROLE NOT FOUND'
        elif not username or not password or not email or not role:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO EMP VALUES (NULL, %s, %s,%s,%s)', (username, password,role ,email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('new-account.html', msg = msg)


@app.route('/login/', methods=['GET', 'POST'])
def Login():
    if 'loggedin' in session:
        return redirect(url_for('home'))
    msg = ''
        # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM EMP WHERE username = %s AND pass = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            cursor.execute('SELECT * FROM chef_projet WHERE chef_id = %s', (account['emp_id'],))
            chef = cursor.fetchone()
            session['ischef'] = True if chef else False
            session['loggedin'] = True
            session['emp_id'] = account['emp_id']
            session['username'] = account['username']
            session['email'] = account['email']
            # Redirect to home page
            print(session['ischef'])
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('user-login.html',msg = msg)

@app.route('/logout')
def Logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('emp_id', None)
   session.pop('username', None)
   session.pop('email', None)
   # Redirect to login page
   return redirect(url_for('Login'))



@app.route('/projects')
def Projects():
    #Get all project from database
    return render_template('project.html', title="Projects")

@app.route('/project-details/<int:id>')
def projectdetails(id):
    if not 'loggedin' in session:
        return redirect(url_for('Login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM projet WHERE projet_id = %s', (id,))
    # Fetch one record and return result
    projet = cursor.fetchone()
    if projet is None:
        return redirect(url_for('Login'))
    return render_template('project-details.html', title = "Project Details", data = projet)

        

@app.route('/userProfile')
def userProfile():
    if not 'loggedin' in session:
        return redirect(url_for('Login'))

    
        # Check if account exists using MySQL

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT emp_id,fullName,dpt_name,joinDate,email,phone,status FROM emp e INNER JOIN departement d ON e.dpt_id = d.dpt_id WHERE emp_id = %s', (session['emp_id'],))
    account = cursor.fetchone()

    
    cursor.execute('''SELECT tache_id, nomT, priority, dateD, dateF, etat, status, t.projet_id  
                    FROM tache t INNER JOIN projet p ON t.projet_id = p.projet_id
                    INNER JOIN equipe e ON p.equipe_id = e.equipe_id
                    INNER JOIN emp_equipe ee ON e.equipe_id = ee.equipe_id
                    WHERE ee.emp_id = %s''', (session['emp_id'],))

    task = cursor.fetchall()

    
    cursor.execute('''SELECT COUNT(status) as task FROM tache t INNER JOIN projet p ON t.projet_id = p.projet_id
                    INNER JOIN equipe e ON p.equipe_id = e.equipe_id
                    INNER JOIN emp_equipe ee ON e.equipe_id = ee.equipe_id
                    WHERE ee.emp_id = %s''', (session['emp_id'],))
    totalTasks = cursor.fetchone()

    
    cursor.execute('''SELECT COUNT(status) as task FROM tache t INNER JOIN projet p ON t.projet_id = p.projet_id
                    INNER JOIN equipe e ON p.equipe_id = e.equipe_id
                    INNER JOIN emp_equipe ee ON e.equipe_id = ee.equipe_id
                    WHERE ee.emp_id = %s and status = 'On Hold' ''', (session['emp_id'],))
    hold = cursor.fetchone()

    
    cursor.execute('''SELECT COUNT(status) as task FROM tache t INNER JOIN projet p ON t.projet_id = p.projet_id
                    INNER JOIN equipe e ON p.equipe_id = e.equipe_id
                    INNER JOIN emp_equipe ee ON e.equipe_id = ee.equipe_id
                    WHERE ee.emp_id = %s and status = 'Dealy' ''', (session['emp_id'],))
    run = cursor.fetchone()

    
    cursor.execute('''SELECT COUNT(status) as task FROM tache t INNER JOIN projet p ON t.projet_id = p.projet_id
                    INNER JOIN equipe e ON p.equipe_id = e.equipe_id
                    INNER JOIN emp_equipe ee ON e.equipe_id = ee.equipe_id
                    WHERE ee.emp_id = %s and status = 'Completed' ''', (session['emp_id'],))
    finished = cursor.fetchone()

    print(account)
    return render_template('user-profile.html', data = account, taskData = task, totalTasks = totalTasks , running = run, hold = hold, finished = finished)

# API

# @app.route("/api/tasktable")
# def tasktable():
#     if not 'loggedin' in session:
#         return redirect(url_for('Login'))
#     # select = request.args.get('selected')
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute('''SELECT tache_id, nomT, priority, dateD, dateF, etat, status, t.projet_id  
#                     FROM tache t INNER JOIN projet p ON t.projet_id = p.projet_id
#                     INNER JOIN equipe e ON p.equipe_id = e.equipe_id
#                     INNER JOIN emp_equipe ee ON e.equipe_id = ee.equipe_id
#                     WHERE ee.emp_id = %s''', (session['emp_id'],))

#     task = cursor.fetchall()

@app.route("/api/customer_chart")
def customer_chart():
    customer_options = {
    'series': [{
        'name': "Complete",
        'data': [40, 70, 20, 90, 36, 80, 30, 91, 60]
    }, {
        'name': "Doing",
        'data': [80, 30, 50, 20, 76, 40, 20, 51, 10]
    }],
    'colors': ['#3C21F7', '#FFCA1F'],
    'chart': {
        'height': 300,
        'type': 'line',
    },
    'dataLabels': {
        'enabled': False
    },
    'stroke': {
        'curve': 'smooth'
    },
    'xaxis': {
        'categories': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
    },}
    return jsonify(customer_options)

@app.route("/api/chartBar2")
def chartBar2():
    options = {
                'series': [{
                        'name': '',
                        'data': [50, 18, 70, 40, 90, 50],
                        #radius: 12,	
                    },
                    {
                        'name': '',
                        'data': [80, 40, 55, 20, 50, 70]
                    },

                ],
                'chart': {
                    'type': 'bar',
                    'height': 350,

                    'toolbar': {
                        'show': False,
                    },

                },
                'plotOptions': {
                    'bar': {
                        'horizontal': False,
                        'columnWidth': '70%',
                        'borderRadius': 10
                    },

                },
                'states': {
                    'hover': {
                        'filter': 'none',
                    }
                },
                'colors': ['#80ec67', '#fe7d65'],
                'dataLabels': {
                    'enabled': False,
                },
                'markers': {
                    'shape': "circle",
                },


                'legend': {
                    'position': 'top',
                    'horizontalAlign': 'right',
                    'show': False,
                    'fontSize': '12px',
                    'labels': {
                        'colors': '#000000',

                    },
                    'markers': {
                        'width': 18,
                        'height': 18,
                        'strokeWidth': 0,
                        'strokeColor': '#fff',
                        'fillColors': None,
                        'radius': 12,
                    }
                },
                'stroke': {
                    'show': True,
                    'width': 5,
                    'colors': ['transparent']
                },
                'grid': {
                    'borderColor': '#eee',
                },
                'xaxis': {

                    'categories': ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
                    'labels': {
                        'style': {
                            'colors': '#3e4954',
                            'fontSize': '13px',
                            'fontFamily': 'poppins',
                            'fontWeight': 400,
                            'cssClass': 'apexcharts-xaxis-label',
                        },
                    },
                    'crosshairs': {
                        'show': False,
                    }
                },
                'yaxis': {
                    'labels': {
                        'offsetX': -16,
                        'style': {
                            'colors': '#3e4954',
                            'fontSize': '13px',
                            'fontFamily': 'poppins',
                            'fontWeight': 400,
                            'cssClass': 'apexcharts-xaxis-label',
                        },
                    },
                },
                'fill': {
                    'opacity': 1,
                    'colors': ['#00BC8B', '#FFCA1F'],
                },
                'tooltip': {
                    'y': {
                            
                         }
                    },
                'responsive': [{
                    'breakpoint': 575,
                    'options': {
                        'chart': {
                            'height': 250,
                        }
                    },
                }]
            }
    return jsonify(options)


def formatter(val):
    return " " + val + " "
# Error
@app.errorhandler(404)
def page_not_found(error):
    # return 'Erreur'
    return render_template('404.html', title = 'error'), 404


if __name__ == '__main__':
    socketio.run(app, debug=True)