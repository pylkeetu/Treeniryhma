from flask import Blueprint, render_template, request, redirect, session, flash
import db
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register")
def register():
    return render_template("register.html")


@auth_bp.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if not username:
        return "VIRHE"
    if password1 != password2:
        return "VIRHE"

    password_hash = generate_password_hash(password1)

    try:
        db.execute(
            "INSERT INTO employees (username, password_hash) VALUES (?, ?)",
            [username, password_hash]
        )
    except:
        return "VIRHE: tunnus varattu"

    flash("Tunnus luotu onnistuneesti, voit nyt kirjautua sisään.")
    return redirect("/")

@auth_bp.route("/login", methods=["GET", "POST"])
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
        return "VIRHE"

    employee_id = result[0][0]
    password_hash = result[0][1]

    if check_password_hash(password_hash, password):
        session["employee_id"] = employee_id
        session["username"] = username
        return redirect("/")
    else:
        return "VIRHE"
    
@auth_bp.route("/logout")
def logout():
    session.pop("employee_id", None)
    session.pop("username", None)
    return redirect("/")