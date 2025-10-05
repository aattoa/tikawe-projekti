CREATE TABLE users
( username      TEXT PRIMARY KEY NOT NULL
, password_hash TEXT             NOT NULL
, page_visits   INT              NOT NULL);

CREATE TABLE messages
( username TEXT NOT NULL
, content  TEXT NOT NULL
, channel  TEXT NOT NULL
, FOREIGN KEY (username) REFERENCES users (username));
