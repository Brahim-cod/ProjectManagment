from asyncio import tasks
from ntpath import join
from turtle import title
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_mysqldb import MySQL
import MySQLdb
import re
from flask_socketio import SocketIO
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'qOjLneE5QOa8AEF1GQGhQelVN3452Iwf'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
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
def Chat():
    return render_template('message.html', title="Message")

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

@app.route('/newProject', methods=['GET', 'POST'])
def newProject():
    if not 'loggedin' in session:
        return redirect(url_for('Login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM categorie')
    cat = cursor.fetchall()

    cursor.execute("SELECT * FROM equipe WHERE equipe_id not in (select equipe_id from projet) OR equipe_id in (select equipe_id from projet WHERE status = 'On Progress')")
    teams = cursor.fetchall()
    return render_template('new-project.html',title = "New Project", cats = cat, teams = teams)

@app.route('/addProject', methods=['GET', 'POST'])
def addProject():
    if not 'loggedin' in session:
            return redirect(url_for('Login'))
    if request.method == 'POST':
        title =  request.form['title']
        cat =  request.form['category']
        team = request.form['team']
        startDate =  request.form['StartDate']
        endDate =  request.form['EndDate']
        desc = request.form['desc']
        if  startDate > endDate:
            flash('Ended date must be greater than started date!', "Error")
            return redirect(url_for('newProject'))
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''INSERT INTO projet (nomP,datedebut,datefin,descriptionP,cat_id,equipe_id)
                        VALUES (%s,%s,%s,%s,%s,%s)''', (title, startDate, endDate, desc, cat, team, ))
        mysql.connection.commit()
    return redirect(url_for('newProject'))

@app.route('/newTeam')
def Team():
    if not 'loggedin' in session:
        return redirect(url_for('Login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('Select emp_id, fullName, dpt_name from emp e, departement d Where d.dpt_id = e.dpt_id and emp_id not in (select emp_id from emp_equipe where equipe_id not in (select equipe_id from projet where datefin < CURDATE())) and emp_id not in (select chef_id from chef_projet)')
    emps = cursor.fetchall()
    return render_template('new-team.html', emps = emps)

@app.route('/addTeam', methods=['GET', 'POST'])
def addTeam():
    if not 'loggedin' in session:
            return redirect(url_for('Login'))
    if request.method == 'POST':
        nameeq =  request.form['nameeq']
        emps =  request.form.getlist('empscheck')
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''INSERT INTO equipe (nomEQ,chef_id)
                          VALUES (%s,%s)''', (nameeq, session['emp_id'], ))
        mysql.connection.commit()

        cursor.execute('SELECT MAX(equipe_id) as id FROM equipe')
        id = cursor.fetchone()
        for item in emps:
            cursor.execute('''INSERT INTO emp_equipe (emp_id,equipe_id)
                          VALUES (%s,%s)''', (item, id['id'], ))
            mysql.connection.commit()
        flash('You have successfully added new Team!', "new")
    return redirect(url_for('Team'))


@app.route('/task/update/<int:id>', methods=['GET', 'POST'])
def taskUpdate(id):
    if not 'loggedin' in session:
        return redirect(url_for('Login'))
    if request.method == 'POST' and 'taskName' in request.form and 'taskPriority' in request.form and 'dateStart' in request.form and 'dateFinish' in request.form and 'taskEtat' in request.form and 'taskStatus' in request.form:
        # Create variables for easy access
        name = request.form['taskName']
        finish = request.form['dateFinish']
        start = request.form['dateStart']
        etat = request.form['taskEtat']
        priority = request.form['taskPriority']
        status = request.form['taskStatus']
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
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM departement')
    depts = cursor.fetchall()
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST':
        # Create variables for easy access
        username = request.form['username']
        fullname = request.form['fullname']
        phone = request.form['phone']
        dept = request.form['dept']
        joindate = request.form['joindate']
        password = request.form['password']
        email = request.form['email']
         # Check if account exists using MySQL
        cursor.execute('SELECT * FROM EMP WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not  re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not  re.fullmatch(r'[A-Za-z0-9]{8,}', password):
            msg = 'Password must contain at least 8 characters and numbers!'
        elif not username or not password or not email or not fullname or not phone or not dept or not joindate:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO EMP (fullName,dpt_id,joinDate,username,email,pass,phone) VALUES (%s,%s,%s,%s,%s,%s,%s)', (fullname, dept, joindate, username, email, password, phone, ))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
   
    
    # Show registration form with message (if any)
    return render_template('new-account.html', msg = msg, title = 'Add Employee' , depts = depts)


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
            cursor.execute('UPDATE emp set status = true WHERE emp_id = %s', (session['emp_id'],))
            mysql.connection.commit()
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('user-login.html',msg = msg)

@app.route('/logout')
def Logout():
    # Remove session data, this will log the user out
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE emp set status = false WHERE emp_id = %s', (session['emp_id'],))
    mysql.connection.commit()
    session.pop('loggedin', None)
    session.pop('emp_id', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('ischef', None)
    # Redirect to login page
    return redirect(url_for('Login'))

@app.route('/calendar')
def Calendar():
    if not 'loggedin' in session:
        return redirect(url_for('Login'))
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # cursor.execute('SELECT * FROM event WHERE emp_id = %s', (session['emp_id'],))
    # events = cursor.fetchall()
    return render_template('calendar.html', title = 'Calendar')


@app.route('/api/calendar')
def events():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM event WHERE emp_id = %s', (session['emp_id'],))
    events = cursor.fetchall()
    

    cursor.execute('select * from tache where emp_id = %s', (session['emp_id'],))
    tasks =  cursor.fetchall()
    e = []
    for item in events:
            i = {
                    'title': item['nomE'],
                    'start': item['dateD'].strftime('%Y-%m-%d'),
                    'end': item['dateF'].strftime('%Y-%m-%d')
                }
            e.append(i)

    for item in tasks:
        i = {
                'title': item['nomT'],
                'start': item['dateD'].strftime('%Y-%m-%d'),
            }
        y = {
                'title': item['nomT'],
                'start': item['dateF'].strftime('%Y-%m-%d'),
            }
        e.append(i)
        e.append(y)
    es = {
        'headerToolbar': {
            'left': 'prev,next today',
            'center': 'title',
            'right': 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
        },
        'initialDate': datetime.today().strftime('%Y-%m-%d'),
        'navLinks': True, 
        'businessHours': True, 
        'editable': True,
        'selectable': True,
        'events': [{
                'title': 'Business Lunch',
                'start': '2020-09-03T13:00:00',
                'constraint': 'businessHours'
            },
            {
                'title': 'Meeting',
                'start': '2020-09-13T11:00:00',
                'constraint': 'availableForMeeting', 
                'color': '#257e4a'
            },
            {
                'title': 'Conference',
                'start': '2020-09-01T11:00:00',
                'end': '2020-09-01T14:00:00'
            },
            {
                'title': 'Party',
                'start': '2020-09-29T20:00:00'
            },
            {
                'groupId': 'availableForMeeting',
                'start': '2020-09-11T10:00:00',
                'end': '2020-09-11T16:00:00',
                'display': 'background'
            },
            {
                'groupId': 'availableForMeeting',
                'start': '2020-09-13T10:00:00',
                'end': '2020-09-13T16:00:00',
                'display': 'background'
            },
            {
                'start': '2020-09-24',
                'end': '2020-09-28',
                'overlap': False,
                'display': 'background',
                'color': '#ff9f89'
            },
            {
                'start': '2020-09-06',
                'end': '2020-09-08',
                'overlap': False,
                'display': 'background',
                'color': '#ff9f89'
            }
        ]
        }
    return jsonify(es)
    

@app.route('/projects')
def Projects():
    #Get all project from database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM projet')
    projets = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM projet WHERE status = 'On Progress'")
    onp = cursor.fetcone()

    cursor.execute("SELECT COUNT(*) FROM projet WHERE status = 'Pending'")
    pd = cursor.fetcone()

    cursor.execute("SELECT COUNT(*) FROM projet WHERE status = 'Completed'")
    cm = cursor.fetcone()

    return render_template('project.html', title="Projects", projets = projets, onp = onp, pd = pd, cm = cm)

@app.route('/project-details/<int:id>')
def projectdetails(id):
    if not 'loggedin' in session:
        return redirect(url_for('Login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM projet WHERE projet_id = %s', (id,))
    # Fetch one record and return result
    projet = cursor.fetchone()
    if projet is None:
        return render_template('404.html')    
    return render_template('project-details.html', title = "Project Details", data = projet)

        

@app.route('/userProfile')
def userProfile():
    if not 'loggedin' in session:
        return redirect(url_for('Login'))


    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT emp_id,fullName,dpt_name,joinDate,email,phone,status FROM emp e INNER JOIN departement d ON e.dpt_id = d.dpt_id WHERE emp_id = %s', (session['emp_id'],))
    account = cursor.fetchone()

    
    cursor.execute('''SELECT tache_id, nomT, priority, dateD, dateF, etat, status, projet_id  
                    FROM tache WHERE emp_id = %s''', (session['emp_id'],))

    task = cursor.fetchall()

    
    cursor.execute('''SELECT COUNT(status) as task FROM tache WHERE emp_id = %s''', (session['emp_id'],))
    totalTasks = cursor.fetchone()

    
    cursor.execute('''SELECT COUNT(status) as task FROM tache WHERE emp_id = %s and status = 'On Hold' ''', (session['emp_id'],))
    hold = cursor.fetchone()

    
    cursor.execute('''SELECT COUNT(status) as task FROM tache WHERE emp_id = %s and status = 'Dealy' ''', (session['emp_id'],))
    run = cursor.fetchone()

    
    cursor.execute('''SELECT COUNT(status) as task FROM tache WHERE emp_id = %s and status = 'Completed' ''', (session['emp_id'],))
    finished = cursor.fetchone()

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
    return render_template('404.html'), 404


if __name__ == '__main__':
    socketio.run(app, debug=True)