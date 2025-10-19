CREATE TABLE users
( username      TEXT PRIMARY KEY NOT NULL
, password_hash TEXT             NOT NULL
, page_visits   INTEGER          NOT NULL);

CREATE TABLE messages
( id       INTEGER PRIMARY KEY NOT NULL
, username TEXT                NOT NULL
, content  TEXT                NOT NULL
, channel  TEXT                NOT NULL
, likes    INTEGER             NOT NULL
, FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE);

CREATE TABLE likes
( message_id INTEGER NOT NULL
, username   TEXT    NOT NULL
, FOREIGN KEY (message_id) REFERENCES messages (id) ON DELETE CASCADE
, FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE);

CREATE TABLE categories
( message_id INTEGER NOT NULL
, category   TEXT    NOT NULL
, FOREIGN KEY (message_id) REFERENCES messages (id) ON DELETE CASCADE);
