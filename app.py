import os.path
import sqlite3
import flask
import werkzeug.security

DB = 'database.db'

def connect():
    db = sqlite3.connect(DB)
    db.execute('PRAGMA foreign_keys = ON')
    return db

def execute(sql, params=None):
    db = connect()
    try:
        db.execute(sql, params)
        db.commit()
    finally:
        db.close()

def query(sql):
    db = connect()
    try:
        results = db.execute(sql).fetchall()
    finally:
        db.close()
    return results

if not os.path.exists(DB):
    execute('''
            CREATE TABLE users
            ( username TEXT PRIMARY KEY NOT NULL
            , password_hash TEXT NOT NULL);
            ''')
    execute('''
            CREATE TABLE messages
            ( username TEXT NOT NULL
            , content TEXT NOT NULL
            , FOREIGN KEY (username) REFERENCES users (username));
            ''')

app = flask.Flask(__name__)

@app.route('/channel/<name>')
def channel(name):
    messages = query('SELECT * FROM messages')
    return flask.render_template('index.html', channel=name, count=len(messages), messages=messages)

@app.route('/')
def index():
    return flask.redirect('/channel/default')

@app.route('/register')
def register():
    return flask.render_template('register.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    username = flask.request.form['username']
    password = flask.request.form['password']

    password_hash = werkzeug.security.generate_password_hash(password)

    try:
        sql = 'INSERT INTO users (username, password_hash) VALUES (?, ?)'
        execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return 'Username already taken'

    return flask.redirect("/")
