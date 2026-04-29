import db
from werkzeug.security import generate_password_hash, check_password_hash


def register():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if not username or len(username) > 16:
        abort(403)

    if password1 != password2:
        flash("Salasanat eivät täsmää")
        return render_template("register.html")

    try:
        db.execute(
            "INSERT INTO employees (username, password_hash) VALUES (?, ?)",
            [username, generate_password_hash(password1)]
        )
    except:
        flash("Käyttäjä on jo olemassa")
        return render_template("register.html")

    return redirect("/")


def login():
    username = request.form["username"]
    password = request.form["password"]

    result = db.query(
        "SELECT id, password_hash FROM employees WHERE username = ?",
        [username]
    )

    if len(result) == 1:
        user_id, password_hash = result[0]

        if check_password_hash(password_hash, password):
            session["employee_id"] = user_id
            session["username"] = username
            return redirect("/")

    flash("Väärä tunnus tai salasana")
    return render_template("login.html")


def get_user_page(user_id):
    user = db.query(
        "SELECT id, username FROM employees WHERE id = ?",
        [user_id]
    )

    shifts_list = db.query(
        "SELECT * FROM shifts WHERE employee_id = ?",
        [user_id]
    )

    stats = db.query(
        """SELECT COUNT(*) as count,
                  COALESCE(AVG(participants), 0) as avg
           FROM shifts WHERE employee_id = ?""",
        [user_id]
    )[0]

    return {"user": user[0] if user else None,
            "shifts": shifts_list,
            "stats": stats}