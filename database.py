from dataclasses import dataclass
import sqlite3
import werkzeug.security

@dataclass
class Message:
    id: int
    username: str
    content: str
    channel: str
    likes: int

def __connect():
    db = sqlite3.connect('database.db')
    db.execute('PRAGMA foreign_keys = ON')
    db.row_factory = lambda _cursor, row: row if len(row) != 1 else row[0]
    return db

def __execute(sql, args=None):
    db = __connect()
    try:
        db.execute(sql, [] if args is None else args)
        db.commit()
    finally:
        db.close()

def __query(sql, args=None, one=False):
    db = __connect()
    try:
        result = db.execute(sql, [] if args is None else args)
        return result.fetchone() if one else result.fetchall()
    finally:
        db.close()

def message(msg_id: int) -> Message:
    sql = 'SELECT * FROM messages WHERE id = ?'
    message = __query(sql, [msg_id], one=True)
    return message and Message(*message)

def message_categories(msg_id: int) -> list[str]:
    sql = 'SELECT category FROM categories WHERE message_id = ?'
    return __query(sql, [msg_id])

def delete_message(msg_id: int) -> None:
    sql = 'DELETE FROM messages WHERE id = ?'
    __execute(sql, [msg_id])

def edit_message(msg_id: int, content: str) -> None:
    sql = 'UPDATE messages SET content = ? WHERE id = ?'
    __execute(sql, [content, msg_id])

def add_message_category(msg_id: int, category: str) -> None:
    sql = 'INSERT INTO categories (message_id, category) VALUES (?, ?)'
    __execute(sql, [msg_id, category])

def user_messages(username: str) -> list[Message]:
    sql = 'SELECT * FROM messages WHERE username = ?'
    return [Message(*fields) for fields in __query(sql, [username])]

def channel_messages(channel: str) -> list[Message]:
    sql = 'SELECT * FROM messages WHERE channel = ?'
    return [Message(*fields) for fields in __query(sql, [channel])]

def category_messages(category: str) -> list[Message]:
    sql = 'SELECT message_id FROM categories WHERE category = ?'
    return [message(msg_id) for msg_id in __query(sql, [category])]

def categories() -> list[str]:
    return __query('SELECT DISTINCT category FROM categories')

def increment_user_visits(username: str) -> int:
    sql = 'UPDATE users SET page_visits = page_visits + 1 WHERE username = ?'
    __execute(sql, [username])
    sql = 'SELECT page_visits FROM users WHERE username = ?'
    return __query(sql, [username], one=True)

def user_total_likes(username: str) -> int:
    sql = 'SELECT TOTAL(likes) FROM messages WHERE username = ?'
    return int(__query(sql, [username], one=True))

def user_post_message(username: str, content: str, channel: str) -> None:
    sql = 'INSERT INTO messages (id, username, content, channel, likes) VALUES (NULL, ?, ?, ?, 0)'
    __execute(sql, [username, content, channel])

def search_channels(term: str) -> list[str]:
    sql = 'SELECT DISTINCT channel FROM messages WHERE instr(channel, ?) > 0'
    return __query(sql, [term])

def is_valid_login(username: str, password: str) -> bool:
    sql = 'SELECT password_hash FROM users WHERE username = ?'
    result = __query(sql, [username], one=True)
    return result and werkzeug.security.check_password_hash(result, password)

def register_user(username: str, password: str) -> bool:
    try:
        sql = 'INSERT INTO users (username, password_hash, page_visits) VALUES (?, ?, 0)'
        __execute(sql, [username, werkzeug.security.generate_password_hash(password)])
        return True
    except sqlite3.IntegrityError:
        return False

def has_user_liked_message(username: str, msg_id: int) -> bool:
    sql = 'SELECT COUNT(*) FROM likes WHERE message_id = ? and username = ?'
    return __query(sql, [msg_id, username], one=True) != 0

def toggle_message_like(username: str, msg_id: int) -> None:
    if has_user_liked_message(username, msg_id):
        sql = 'DELETE FROM likes WHERE message_id = ? and username = ?'
        __execute(sql, [msg_id, username])
        sql = 'UPDATE messages SET likes = likes - 1 WHERE id = ?'
        __execute(sql, [msg_id])
    else:
        sql = 'INSERT INTO likes (message_id, username) VALUES (?, ?)'
        __execute(sql, [msg_id, username])
        sql = 'UPDATE messages SET likes = likes + 1 WHERE id = ?'
        __execute(sql, [msg_id])

def delete_account(username: str) -> None:
    sql = 'DELETE FROM users WHERE username = ?'
    __execute(sql, [username])
