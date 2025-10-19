from dataclasses import dataclass
import sqlite3
import werkzeug.security

@dataclass
class Message:
    username: str
    content: str
    channel: str
    likes: int
    rowid: int

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

def message(rowid: int) -> Message:
    sql = 'SELECT * FROM messages WHERE rowid = ?'
    message = __query(sql, [rowid], one=True)
    return message and Message(*message, rowid)

def message_categories(rowid: int) -> list[str]:
    sql = 'SELECT category FROM categories WHERE message_rowid = ?'
    return __query(sql, [rowid])

def delete_message(rowid: int) -> None:
    sql = 'DELETE FROM messages WHERE rowid = ?'
    __execute(sql, [rowid])
    sql = 'DELETE FROM categories WHERE message_rowid = ?'
    __execute(sql, [rowid])

def edit_message(rowid: int, content: str) -> None:
    sql = 'UPDATE messages SET content = ? WHERE rowid = ?'
    __execute(sql, [content, rowid])

def add_message_category(rowid: int, category: str) -> None:
    sql = 'INSERT INTO categories (message_rowid, category) VALUES (?, ?)'
    __execute(sql, [rowid, category])

def user_messages(username: str) -> list[Message]:
    sql = 'SELECT *, rowid FROM messages WHERE username = ?'
    return [Message(*fields) for fields in __query(sql, [username])]

def channel_messages(channel: str) -> list[Message]:
    sql = 'SELECT *, rowid FROM messages WHERE channel = ?'
    return [Message(*fields) for fields in __query(sql, [channel])]

def category_messages(category: str) -> list[Message]:
    sql = 'SELECT message_rowid FROM categories WHERE category = ?'
    return [message(rowid) for rowid in __query(sql, [category])]

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
    sql = 'INSERT INTO messages (username, content, channel, likes) VALUES (?, ?, ?, 0)'
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

def has_user_liked_message(username: str, rowid: int) -> bool:
    sql = 'SELECT COUNT(*) FROM likes WHERE message_rowid = ? and username = ?'
    return __query(sql, [rowid, username], one=True) != 0

def toggle_message_like(username: str, rowid: int) -> None:
    if has_user_liked_message(username, rowid):
        sql = 'DELETE FROM likes WHERE message_rowid = ? and username = ?'
        __execute(sql, [rowid, username])
        sql = 'UPDATE messages SET likes = likes - 1 WHERE rowid = ?'
        __execute(sql, [rowid])
    else:
        sql = 'INSERT INTO likes (message_rowid, username) VALUES (?, ?)'
        __execute(sql, [rowid, username])
        sql = 'UPDATE messages SET likes = likes + 1 WHERE rowid = ?'
        __execute(sql, [rowid])
