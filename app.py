from flask import Flask, redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    all_jobs = db.query("SELECT * FROM jobs")
    return render_template("index.html", jobs=all_jobs)

@app.route("/job/<int:item_id>")
def show_job(item_id):
    result = db.query("SELECT * FROM jobs WHERE id = ?", [item_id])
    if not result:
        return "Työtä ei löydetty", 404

    job = result[0]
    return render_template("show_job.html", job=job)

@app.route("/job/<int:item_id>/edit", methods=["GET"])
def edit_job_form(item_id):
    result = db.query("SELECT * FROM jobs WHERE id = ?", [item_id])
    if not result:
        return "Työtä ei löydetty", 404
    job = result[0]
    return render_template("edit_job.html", job=job)

@app.route("/job/<int:item_id>/edit", methods=["POST"])
def edit_job(item_id):
    title = request.form["title"]
    description = request.form["description"]
    participants = request.form["participants"]

    db.execute(
        "UPDATE jobs SET title = ?, description = ?, participants = ? WHERE id = ?",
        [title, description, participants, item_id]
    )
    return redirect(f"/job/{item_id}")

@app.route("/job/<int:item_id>/delete", methods=["POST"])
def delete_job(item_id):
    db.execute("DELETE FROM jobs WHERE id = ?", [item_id])
    return render_template("job_deleted.html")

@app.route("/new_shift")
def new_shift():
    return render_template("new_shift.html")

@app.route("/create_shift", methods=["POST"])
def create_shift():
    title = request.form["title"]
    description = request.form["description"]
    participants = request.form["participants"]
    employee_id = session.get("employee_id")

    db.execute(
        "INSERT INTO jobs (title, description, participants, employee_id) VALUES (?, ?, ?, ?)",
        [title, description, participants, employee_id]
    )

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
        db.execute(
            "INSERT INTO employees (username, password_hash) VALUES (?, ?)",
            [username, password_hash]
        )
    except:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    username = request.form["username"]
    password = request.form["password"]

    result = db.query(
        "SELECT id, password_hash FROM employees WHERE username = ?",
        [username]
    )

    if not result:
        return "VIRHE: väärä tunnus tai salasana"

    employee_id = result[0][0]
    password_hash = result[0][1]

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