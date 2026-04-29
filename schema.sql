CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE exercises (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    max_participants INTEGER,
    user_id INTEGER REFERENCES users
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE exercise_categories (
    exercise_id INTEGER,
    category_id INTEGER,
    PRIMARY KEY (exercise_id, category_id),
    FOREIGN KEY (exercise_id) REFERENCES exercises(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE exercise_participants (
    exercise_id INTEGER,
    user_id INTEGER,
    PRIMARY KEY (exercise_id, user_id),
    FOREIGN KEY (exercise_id) REFERENCES exercises(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    exercise_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
);

INSERT INTO categories (name) VALUES ('Lenkki');
INSERT INTO categories (name) VALUES ('Kuntosali (sisä)');
INSERT INTO categories (name) VALUES ('Kuntosali (ulko)');
INSERT INTO categories (name) VALUES ('Tennis');
INSERT INTO categories (name) VALUES ('Padel');
INSERT INTO categories (name) VALUES ('Jalkapallo');
INSERT INTO categories (name) VALUES ('Jääkiekko');
INSERT INTO categories (name) VALUES ('Uinti');
INSERT INTO categories (name) VALUES ('Kamppailulajit');
INSERT INTO categories (name) VALUES ('Crossfit');
INSERT INTO categories (name) VALUES ('Jooga');
INSERT INTO categories (name) VALUES ('Pyöräily');