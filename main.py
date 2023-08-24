import sqlite3
import os

from flask import Flask, render_template, request, flash, session, redirect, url_for, abort, jsonify
from DataBase import DataBase
import datetime

DATABASE = '/tmp/base.db'
DEBUG = True
SECRET_KEY = "FlaskTimer1"

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update({'DATABASE': os.path.join(app.root_path, 'base.db')})

def connect_db():
    con = sqlite3.connect(app.config['DATABASE'])
    con.row_factory = sqlite3.Row
    return con

def create_db():
    db = connect_db()
    with open('sq_db.sql', 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

menu = [
    {'name': 'Home', 'url': '/'},
    {'name': 'About', 'url': 'about'},
    {'name': 'Contacts', 'url': 'contacts'},
    {'name': 'Login', 'url': 'login'},
    {'name': 'Registration', 'url': 'registration'},
    {'name': 'Post', 'url': 'add_post'}
]

users = {
    'admin': {'password': 'admin', 'email': 'admin@gmail.com'}
}

def time_left(target_date):
    current_date = datetime.datetime.now()
    time_difference = target_date - current_date

    time_difference_ = datetime.timedelta(days=time_difference.days,
                                          seconds=time_difference.seconds)

    return time_difference_

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        target_date_str = request.form['target_date']
        if target_date_str:
            target_date = datetime.datetime.strptime(target_date_str, '%Y-%m-%d')
        else:
            target_date = datetime.datetime(2023, 12, 31)
    else:
        target_date = datetime.datetime(2023, 12, 31)

    time_difference = time_left(target_date)
    return render_template('index.html', title='Home', time_difference=time_difference, menu=menu)

@app.route('/get_target_date', methods=['GET'])
def get_target_date():
    target_date_str = request.args.get('target_date', default='2023-12-31')
    return jsonify({'target_date': target_date_str})

@app.route('/about')
def about():
    return render_template('about.html', title='AboutUs', menu=menu)

@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    context = {}
    if request.method == 'POST':
        if len(request.form['username']) > 1:
            flash('The message was sent successfully!', category='success')
        else:
            flash('Sending error!', category='error')
        context = {
            'username': request.form['username'],
            'email': request.form['email'],
            'message': request.form['message'],
        }

    return render_template('contacts.html', **context, title='Feedback')

@app.route('/profile/<string:username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f'USER {username}'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['email'] = users[username]['email']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Incorrect username or password!')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        email = session['email']
        return render_template('dashboard.html', username=username, email=email)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if username in users:
            return render_template('register.html', error='The username is already taken.'
                                                          'Please choose a different name.')

        users[username] = {'password': password, 'email': email}

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/add_menu_item', methods=['POST'])
def add_menu_item():
    if request.method == 'POST':
        title = request.form['title']
        link = request.form['link']

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute('INSERT INTO menu (title, link) VALUES (?, ?)', (title, link))
        conn.commit()

        cursor.close()
        conn.close()

        return 'Menu item added successfully.'


@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    db_con = connect_db()
    db = DataBase(db_con)

    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        url = request.form['url']

        if len(title) > 0 and len(text) > 0 and len(url) > 0:
            if db.add_post(title, text, url):
                flash('The article was added successfully!', category='success')
            else:
                flash('Error adding an article!', category='error')
        else:
            flash('Please fill in all fields!', category='error')

    return render_template('add_post.html', title='Add Article', menu=db.get_menu())


@app.route('/show_all_posts')
def show_all_posts():
    db_con = connect_db()
    db = DataBase(db_con)
    articles = db.get_posts()
    return render_template('posts.html', title='All Articles', articles=articles)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', title='Page not found', menu=menu), 404


if __name__ == '__main__':
    create_db()
    app.run()




