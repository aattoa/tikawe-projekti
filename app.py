import secrets
import flask
import database

def redirect_prev_channel():
    channel = flask.session.get('channel', 'default')
    return flask.redirect(f'/channel/{channel}')

def require_authentic_request():
    if not flask.session.get('user'):
        flask.abort(403, description='Login required!')
    if flask.request.form.get('csrf') != flask.session.get('csrf'):
        flask.abort(403, description='Cross-site request forgery detected!')

def require_modifiable_message(msg_id):
    if flask.session.get('user') != database.message(msg_id).username:
        flask.abort(403, description='You do not have permission to modify this message!')

def session_set_login(username: str):
    # Random per-login data used to prevent cross-site request forgery
    flask.session['csrf'] = secrets.token_hex(32)
    flask.session['user'] = username

def session_clear_login():
    del flask.session['user']
    del flask.session['csrf']

app = flask.Flask(__name__)
app.secret_key = secrets.token_hex(32)

@app.route('/channel/<channel>')
def channel(channel):
    flask.session['channel'] = channel
    messages = database.channel_messages(channel)
    return flask.render_template(
        'channel.html',
        channel=channel,
        count=len(messages),
        messages=messages)

@app.route('/')
def index():
    return flask.redirect('/channel/default')

@app.route('/register')
def register():
    return flask.render_template('register.html')

@app.route('/login')
def login():
    return flask.render_template('login.html')

@app.route('/logout')
def logout():
    session_clear_login()
    return redirect_prev_channel()

@app.route('/edit/<int:msg_id>')
def edit(msg_id):
    content = database.message(msg_id).content
    return flask.render_template('edit.html', content=content, msg_id=msg_id)

@app.route('/categories/<int:msg_id>')
def categories(msg_id):
    categories = database.message_categories(msg_id)
    message = database.message(msg_id)
    return flask.render_template(
        'categories.html',
        categories=categories,
        message=message,
        msg_id=msg_id)

@app.route('/category_list')
def category_list():
    return flask.render_template('category_list.html', categories=database.categories())

@app.route('/category_search/<category>')
def category_search(category):
    messages = database.category_messages(category)
    return flask.render_template('category_search.html', category=category, messages=messages)

@app.route('/user/<user>')
def user(user):
    messages = database.user_messages(user)
    visits = database.increment_user_visits(user)
    likes = database.user_total_likes(user)
    return flask.render_template(
        'user.html',
        user=user,
        likes=likes,
        visits=visits,
        messages=messages)

@app.route('/api/register', methods=['POST'])
def api_register():
    username = flask.request.form['username']
    password = flask.request.form['password']
    if database.register_user(username, password):
        session_set_login(username)
        return redirect_prev_channel()
    return flask.render_template('error.html', message='Username already taken!')

@app.route('/api/login', methods=['POST'])
def api_login():
    username = flask.request.form['username']
    password = flask.request.form['password']
    if database.is_valid_login(username, password):
        session_set_login(username)
        return redirect_prev_channel()
    return flask.render_template('error.html', message='Invalid username or password!')

@app.route('/api/post/<channel>', methods=['POST'])
def api_post(channel):
    require_authentic_request()
    database.user_post_message(flask.session['user'], flask.request.form['content'], channel)
    return flask.redirect(f'/channel/{channel}')

@app.route('/api/delete/<int:msg_id>', methods=['POST'])
def api_delete(msg_id):
    require_authentic_request()
    require_modifiable_message(msg_id)
    database.delete_message(msg_id)
    return redirect_prev_channel()

@app.route('/api/edit/<int:msg_id>', methods=['POST'])
def api_edit(msg_id):
    require_authentic_request()
    require_modifiable_message(msg_id)
    database.edit_message(msg_id, flask.request.form['content'])
    return redirect_prev_channel()

@app.route('/api/add_category/<int:msg_id>', methods=['POST'])
def api_add_category(msg_id):
    require_authentic_request()
    require_modifiable_message(msg_id)
    database.add_message_category(msg_id, flask.request.form['new_category'])
    return redirect_prev_channel()

@app.route('/api/channel_search', methods=['POST'])
def api_channel_search():
    term = flask.request.form.get('search_term', '')
    channels = database.search_channels(term)
    return flask.render_template('channel_search.html', channels=channels, search_term=term)

@app.route('/api/like/<int:msg_id>', methods=['POST'])
def api_like(msg_id):
    require_authentic_request()
    database.toggle_message_like(flask.session['user'], msg_id)
    return redirect_prev_channel()

@app.route('/api/delete_account', methods=['POST'])
def api_delete_account():
    require_authentic_request()
    database.delete_account(flask.session['user'])
    session_clear_login()
    return redirect_prev_channel()
