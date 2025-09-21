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
        db.execute(sql, [] if params is None else params)
        db.commit()
    finally:
        db.close()

def query(sql, params=None):
    db = connect()
    try:
        results = db.execute(sql, [] if params is None else params).fetchall()
    finally:
        db.close()
    return results

app = flask.Flask(__name__)
app.secret_key = 'TODO: maybe consider setting a proper value for this'

@app.route('/channel/<name>')
def channel(name):
    flask.session['channel'] = name
    sql = 'SELECT rowid, username, content FROM messages WHERE channel = ?'
    messages = query(sql, [name])
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

    return flask.redirect('/')

@app.route('/login')
def login():
    return flask.render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    username = flask.request.form['username']
    password = flask.request.form['password']

    sql = 'SELECT password_hash FROM users WHERE username = ?'
    password_hash = query(sql, [username])[0][0]

    if werkzeug.security.check_password_hash(password_hash, password):
        flask.session['user'] = username
        return flask.redirect('/')
    return 'Invalid username or password!'

@app.route('/logout')
def api_logout():
    del flask.session['user']
    return flask.redirect('/')

@app.route('/api/post/<channel>', methods=['POST'])
def api_post(channel):
    if not flask.session['user']:
        return 'Not logged in!'

    sql = 'INSERT INTO messages (username, content, channel) VALUES (?, ?, ?)'
    execute(sql, [flask.session['user'], flask.request.form['content'], channel])

    return flask.redirect(f'/channel/{channel}')

@app.route('/api/delete/<rowid>')
def api_delete(rowid):
    if not flask.session['user']:
        return 'Not logged in!'

    sql = 'SELECT username FROM messages WHERE rowid = ?'

    if query(sql, [rowid]) != [(flask.session['user'],)]:
        return 'Invalid message id!'

    sql = 'DELETE FROM messages WHERE rowid = ?'
    execute(sql, [rowid])

    channel = flask.session['channel'] or 'default'
    return flask.redirect(f'/channel/{channel}')

@app.route('/edit/<rowid>')
def edit(rowid):
    sql = 'SELECT content FROM messages WHERE rowid = ?'
    content = query(sql, [rowid])[0][0]
    return flask.render_template('edit.html', content=content, rowid=rowid)

@app.route('/api/edit/<rowid>', methods=['POST'])
def api_edit(rowid):
    if not flask.session['user']:
        return 'Not logged in!'

    sql = 'SELECT username FROM messages WHERE rowid = ?'
    if query(sql, [rowid]) != [(flask.session['user'],)]:
        return 'Invalid message id!'

    sql = 'UPDATE messages SET content = ? WHERE rowid = ?'
    execute(sql, [flask.request.form['content'], rowid])

    channel = flask.session['channel'] or 'default'
    return flask.redirect(f'/channel/{channel}')

@app.route('/api/channel_search', methods=['POST'])
def api_channel_search():
    sql = 'SELECT DISTINCT channel FROM messages WHERE instr(channel, ?) > 0'
    search_term = flask.request.form['search_term']
    channels = query(sql, [search_term])
    return flask.render_template('channel_search.html', new=not channels, channels=channels, search_term=search_term)
