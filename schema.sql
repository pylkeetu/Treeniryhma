CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE shifts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    salary INTEGER,
    participants INTEGER,
    employee_id INTEGER REFERENCES employees
);