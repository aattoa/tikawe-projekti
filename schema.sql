CREATE TABLE users
( username      TEXT PRIMARY KEY NOT NULL
, password_hash TEXT             NOT NULL
, page_visits   INT              NOT NULL);

CREATE TABLE categories
( message_rowid INT  NOT NULL
, category      TEXT NOT NULL);

CREATE TABLE messages
( username TEXT NOT NULL
, content  TEXT NOT NULL
, channel  TEXT NOT NULL
, likes    INT  NOT NULL
, FOREIGN KEY (username) REFERENCES users (username));
