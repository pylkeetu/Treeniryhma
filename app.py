from flask import Flask, redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    all_shifts = db.query("SELECT * FROM shifts")
    return render_template("index.html", shifts=all_shifts)

@app.route("/shift/<int:item_id>")
def show_shift(item_id):
    result = db.query("SELECT * FROM shifts WHERE id = ?", [item_id])
    if not result:
        return "Työtä ei löydetty", 404

    shift = result[0]
    return render_template("show_shift.html", shift=shift)

@app.route("/shift/<int:item_id>/edit", methods=["GET"])
def edit_shift_form(item_id):
    if "employee_id" not in session:
        return "Kirjaudu sisään"

    result = db.query("SELECT * FROM shifts WHERE id = ?", [item_id])
    if not result:
        return "Työvuoroa ei löydy", 404

    shift = result[0]

    if shift["employee_id"] != session["employee_id"]:
        return "Ei oikeuksia", 403

    return render_template("edit_shift.html", shift=shift)

@app.route("/shift/<int:item_id>/edit", methods=["POST"])
def edit_shift(item_id):
    if "employee_id" not in session:
        return "Kirjaudu sisään"

    result = db.query("SELECT employee_id FROM shifts WHERE id = ?", [item_id])
    if not result:
        return "Ei löydy", 404

    if result[0][0] != session["employee_id"]:
        return "Ei oikeuksia", 403

    title = request.form["title"]
    description = request.form["description"]
    participants = request.form["participants"]

    db.execute(
        "UPDATE shifts SET title = ?, description = ?, participants = ? WHERE id = ?",
        [title, description, participants, item_id]
    )

    return redirect(f"/shift/{item_id}")

@app.route("/shift/<int:item_id>/delete", methods=["POST"])
def delete_shift(item_id):
    if "employee_id" not in session:
        return "Kirjaudu sisään"

    result = db.query("SELECT employee_id FROM shifts WHERE id = ?", [item_id])
    if not result:
        return "Ei löydy", 404

    # 🔴 TÄRKEIN RIVI
    if result[0][0] != session["employee_id"]:
        return "Ei oikeuksia", 403

    db.execute("DELETE FROM shifts WHERE id = ?", [item_id])
    return redirect("/")

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
        "INSERT INTO shifts (title, description, participants, employee_id) VALUES (?, ?, ?, ?)",
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

    return redirect("/")

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