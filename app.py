import secrets
import sqlite3
import flask
import werkzeug.security

def connect():
    db = sqlite3.connect('database.db')
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

def redirect_prev_channel():
    channel = flask.session.get('channel', 'default')
    return flask.redirect(f'/channel/{channel}')

def require_authentic_request():
    if flask.request.form.get('csrf') != flask.session.get('csrf'):
        flask.abort(403, description='Cross-site request forgery detected!')

def require_login():
    if not flask.session.get('user'):
        flask.abort(403, description='Login required!')

def require_modifiable_message(rowid):
    sql = 'SELECT username FROM messages WHERE rowid = ?'
    if query(sql, [rowid]) != [(flask.session.get('user'),)]:
        flask.abort(403, description='You do not have permission to modify this message!')

app = flask.Flask(__name__)
app.secret_key = 'TODO: maybe consider setting a proper value for this'

@app.route('/channel/<name>')
def channel(name):
    flask.session['channel'] = name
    sql = 'SELECT rowid, username, content, likes FROM messages WHERE channel = ?'
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
        sql = 'INSERT INTO users (username, password_hash, page_visits) VALUES (?, ?, 0)'
        execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return 'Username already taken'

    return redirect_prev_channel()

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
        flask.session['csrf'] = secrets.token_hex(32) # Random per-user data to prevent cross-site request forgery
        return redirect_prev_channel()
    return 'Invalid username or password!'

@app.route('/logout')
def api_logout():
    del flask.session['user']
    del flask.session['csrf']
    return redirect_prev_channel()

@app.route('/api/post/<channel>', methods=['POST'])
def api_post(channel):
    require_authentic_request()
    require_login()
    sql = 'INSERT INTO messages (username, content, channel, likes) VALUES (?, ?, ?, 0)'
    execute(sql, [flask.session.get('user'), flask.request.form.get('content'), channel])
    return flask.redirect(f'/channel/{channel}')

@app.route('/api/delete/<rowid>', methods=['POST'])
def api_delete(rowid):
    require_authentic_request()
    require_modifiable_message(rowid)
    sql = 'DELETE FROM messages WHERE rowid = ?'
    execute(sql, [rowid])
    return redirect_prev_channel()

@app.route('/edit/<rowid>')
def edit(rowid):
    sql = 'SELECT content FROM messages WHERE rowid = ?'
    content = query(sql, [rowid])[0][0]
    return flask.render_template('edit.html', content=content, rowid=rowid)

@app.route('/api/edit/<rowid>', methods=['POST'])
def api_edit(rowid):
    require_authentic_request()
    require_modifiable_message(rowid)
    sql = 'UPDATE messages SET content = ? WHERE rowid = ?'
    execute(sql, [flask.request.form.get('content'), rowid])
    return redirect_prev_channel()

@app.route('/api/channel_search', methods=['POST'])
def api_channel_search():
    sql = 'SELECT DISTINCT channel FROM messages WHERE instr(channel, ?) > 0'
    search_term = flask.request.form.get('search_term', '')
    channels = query(sql, [search_term])
    return flask.render_template('channel_search.html', new=not channels, channels=channels, search_term=search_term)

@app.route('/api/like/<rowid>', methods=['POST'])
def api_like(rowid):
    require_login()
    require_authentic_request()
    sql = 'UPDATE messages SET likes = likes + 1 WHERE rowid = ?'
    execute(sql, [rowid])
    return redirect_prev_channel()

@app.route('/user/<user>')
def user(user):
    sql = 'SELECT content, channel FROM messages WHERE username = ?'
    messages = query(sql, [user])
    sql = 'UPDATE users SET page_visits = page_visits + 1 WHERE username = ?'
    execute(sql, [user])
    sql = 'SELECT page_visits FROM users WHERE username = ?'
    visits = query(sql, [user])[0][0]
    sql = 'SELECT SUM(likes) FROM messages WHERE username = ?'
    likes = query(sql, [user])[0][0]
    return flask.render_template('user.html', user=user, likes=likes, visits=visits, messages=messages)
