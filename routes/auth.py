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
    if "employee_id" in session:
        return redirect("/")

    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    result = db.query(
        "SELECT id, password_hash FROM employees WHERE username = ?",
        [username]
    )

    if not result:
        flash("Väärä käyttäjätunnus tai salasana", "error")
        return redirect("/login")

    employee_id = result[0]["id"]
    password_hash = result[0]["password_hash"]

    if check_password_hash(password_hash, password):
        session["employee_id"] = employee_id
        session["username"] = username

        flash("Kirjautuminen onnistui", "success")
        return redirect("/")
    else:
        flash("Väärä käyttäjätunnus tai salasana", "error")
        return redirect("/login")
    
@auth_bp.route("/logout")
def logout():
    session.pop("employee_id", None)
    session.pop("username", None)
    return redirect("/")

@auth_bp.route("/user/<int:user_id>")
def user_page(user_id):

    user = db.query(
        "SELECT id, username FROM employees WHERE id = ?",
        [user_id]
    )

    if not user:
        return "Käyttäjää ei löydy", 404

    shifts = db.query(
        "SELECT * FROM shifts WHERE employee_id = ?",
        [user_id]
    )

    stats = db.query(
        """SELECT 
            COUNT(*) as count,
            COALESCE(AVG(participants), 0) as avg_participants
        FROM shifts
        WHERE employee_id = ?""",
        [user_id]
    )[0]

    return render_template("user.html",
                         user=user[0],
                         shifts=shifts,
                         stats=stats)