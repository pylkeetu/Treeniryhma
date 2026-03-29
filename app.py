import sqlite3
from flask import Flask, redirect, render_template, request, session
from werkzeug.security import generate_password_hash,check_password_hash
import config
import db

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/new_shift")
def new_shift():
    return render_template("new_shift.html")

@app.route("/create_shift", methods={"POST"})
def create_shift():
    title = request.form["title"]
    description = request.form["description"]
    participants =  request.form["participants"]
    employee_id = session.get("employee_id")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    sql = """INSERT INTO jobs (title, description, participants, employee_id) 
                VALUES (?, ?, ?, ?)"""
    c.execute(sql, [title, description, participants, employee_id ])

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if not username:
        return "VIRHE: käyttäjätunnus ei voi olla tyhjä"
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"

    password_hash = generate_password_hash(password1)

    try:
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        sql = "INSERT INTO employees (username, password_hash) VALUES (?, ?)"
        c.execute(sql, [username, password_hash])
        conn.commit()
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"
    finally:
        conn.close()

    return "Tunnus luotu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
    
        sql = "SELECT id, password_hash FROM employees WHERE username = ?"
        result = db.query(sql, [username])[0]
        employee_id = result[0]
        password_hash = result[1]

        if check_password_hash(password_hash, password):
            session["employee_id"] = employee_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    session.pop("employee_id", None)
    session.pop("username", None)
    return redirect("/")