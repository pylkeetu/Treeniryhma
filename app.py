import secrets, config, db, security, sqlite3
from datetime import datetime, timezone, timedelta

from flask import (
    Flask, render_template, request, redirect,
    session, flash, abort
)

app = Flask(__name__)
app.secret_key = config.secret_key

# CSRF + LOGIN HELPERS

@app.before_request
def create_csrf():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)


def check_csrf():
    if request.form.get("csrf_token") != session.get("csrf_token"):
        abort(403)


def require_login():
    if "user_id" not in session:
        abort(403)

# AUTH

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    check_csrf()

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
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            [username, security.hash_password(password1)]
        )
    except sqlite3.IntegrityError:
        flash("Käyttäjätunnus on jo varattu")
        return render_template("register.html")

    flash("Tunnus luotu onnistuneesti")
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    check_csrf()

    username = request.form["username"]
    password = request.form["password"]

    result = db.query(
        "SELECT id, password_hash FROM users WHERE username = ?",
        [username]
    )

    if len(result) == 1:
        user_id, password_hash = result[0]

        if security.verify_password(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")

    flash("Väärä tunnus tai salasana")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# USER PAGE

@app.route("/user/<int:user_id>")
def user_page(user_id):

    user = db.query(
        "SELECT id, username FROM users WHERE id = ?",
        [user_id]
    )

    if not user:
        abort(404)

    exercises = db.query(
        "SELECT * FROM exercises WHERE user_id = ?",
        [user_id]
    )
    
    exercise_count = db.query(
    "SELECT COUNT(*) AS count FROM exercises WHERE user_id = ?",
    [user_id]
    )[0]["count"]

    avg = db.query("""
    SELECT COALESCE(AVG(participant_count), 0) AS avg_participants
    FROM (
    SELECT COUNT(ep.user_id) AS participant_count
    FROM exercises e 
    LEFT JOIN exercise_participants ep
    ON e.id = ep.exercise_id
    WHERE e.user_id = ?
    GROUP BY e.id)""", 
    [user_id])[0]["avg_participants"]

    stats = {"count": exercise_count,
            "avg_participants": avg
            }

    join_count = db.query(
        """SELECT COUNT(*) as count
        FROM exercise_participants
        WHERE user_id = ?""",
        [user_id]
    )[0]

    return render_template(
        "user.html",
        user=user[0],
        exercises=exercises,
        stats=stats,
        join_count=join_count
    )

# HOME

@app.route("/")
def index():
    exercises = db.query("SELECT * FROM exercises ORDER BY id DESC")
    users = db.query("SELECT * FROM users ORDER BY username")

    return render_template(
        "index.html",
        exercises=exercises,
        users=users
    )

# EXERCISE PAGE

@app.route("/exercise/<int:item_id>")
def show_exercise(item_id):

    exercise = db.query("""
        SELECT exercises.*, users.username
        FROM exercises
        JOIN users ON exercises.user_id = users.id
        WHERE exercises.id = ?
    """, [item_id])

    if not exercise:
        abort(404)

    exercise = exercise[0]

    categories = db.query("""
        SELECT categories.name
        FROM categories
        JOIN exercise_categories
        ON categories.id = exercise_categories.category_id
        WHERE exercise_categories.exercise_id = ?
    """, [item_id]) or []

    comments = db.query("""
        SELECT comments.*, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.exercise_id = ?
        ORDER BY comments.id DESC
    """, [item_id]) or []

    participants = db.query("""
        SELECT users.username
        FROM exercise_participants
        JOIN users ON users.id = exercise_participants.user_id
        WHERE exercise_participants.exercise_id = ?
    """, [item_id]) or []


    user_id = session.get("user_id")

    is_participant = False

    if user_id:
        result = db.query("""
            SELECT 1 FROM exercise_participants
            WHERE exercise_id = ? AND user_id = ?
        """, [item_id, user_id])

        is_participant = len(result) > 0

    return render_template(
        "show_exercise.html",
        exercise=exercise,
        categories=categories,
        comments=comments,
        participants=participants,
        is_participant=is_participant
    )

# CREATE EXERCISE

@app.route("/new_exercise")
def new_exercise():
    require_login()
    categories = db.query("SELECT * FROM categories")
    return render_template("new_exercise.html", categories=categories)


@app.route("/create_exercise", methods=["POST"])
def create_exercise():
    require_login()
    check_csrf()

    description = request.form["description"]
    max_participants = request.form["participants"]
    category_id = request.form["category"]

    cat = db.query(
        "SELECT name FROM categories WHERE id = ?",
        [category_id]
    )

    if not cat:
        abort(403)

    title = cat[0]["name"]

    exercise_id = db.execute(
        """INSERT INTO exercises (title, description, max_participants, user_id)
           VALUES (?, ?, ?, ?)""",
        [title, description, max_participants, session["user_id"]]
    )

    db.execute(
        "INSERT INTO exercise_categories (exercise_id, category_id) VALUES (?, ?)",
        [exercise_id, category_id]
    )

    return redirect("/")

# EDIT EXERCISE

@app.route("/exercise/<int:item_id>/edit", methods=["GET", "POST"])
def edit_exercise(item_id):
    require_login()

    exercise = db.query(
        "SELECT * FROM exercises WHERE id = ?",
        [item_id]
    )

    if not exercise:
        abort(404)

    if exercise[0]["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        categories = db.query("SELECT * FROM categories")
        return render_template(
            "edit_exercise.html",
            exercise=exercise[0],
            categories=categories
        )

    check_csrf()

    description = request.form["description"]
    max_participants = request.form["participants"]
    category_id = request.form["category"]

    cat = db.query(
        "SELECT name FROM categories WHERE id = ?",
        [category_id]
    )

    if not cat:
        abort(403)

    title = cat[0]["name"]

    db.execute(
        """UPDATE exercises
           SET title = ?, description = ?, max_participants = ?
           WHERE id = ?""",
        [title, description, max_participants, item_id]
    )

    return redirect(f"/exercise/{item_id}")

# DELETE EXERCISE

@app.route("/exercise/<int:item_id>/delete", methods=["POST"])
def delete_exercise(item_id):
    require_login()
    check_csrf()

    db.execute("DELETE FROM exercise_categories WHERE exercise_id = ?", [item_id])
    db.execute("DELETE FROM exercises WHERE id = ?", [item_id])

    return redirect("/")

# COMMENT EXERCISE

@app.route("/exercise/<int:exercise_id>/comment", methods=["POST"])
def add_comment(exercise_id):
    require_login()
    check_csrf()

    content = request.form["content"]

    if len(content) > 100:
        abort(403)

    db.execute(
        """INSERT INTO comments (content, user_id, exercise_id)
           VALUES (?, ?, ?)""",
        [content, session["user_id"], exercise_id]
    )

    return redirect(f"/exercise/{exercise_id}")

# JOIN EXERCISE

@app.route("/exercise/<int:exercise_id>/join", methods=["POST"])
def join_exercise(exercise_id):
    require_login()

    user_id = session["user_id"]

    exercise = db.query(
        "SELECT user_id FROM exercises WHERE id = ?",
        [exercise_id]
    )[0]

    if exercise["user_id"] == user_id:
        abort(403)

    existing = db.query("""
        SELECT 1 FROM exercise_participants
        WHERE exercise_id = ? AND user_id = ?
    """, [exercise_id, user_id])

    if not existing:
        db.execute("""
            INSERT INTO exercise_participants (exercise_id, user_id)
            VALUES (?, ?)
        """, [exercise_id, user_id])

    return redirect(f"/exercise/{exercise_id}")

# TIME FILTER FOR COMMENTS

def localtime(value):
    if not value:
        return ""

    if isinstance(value, str):
        value = datetime.fromisoformat(value)

    finland = timezone(timedelta(hours=3))
    return value.replace(tzinfo=timezone.utc)\
                .astimezone(finland)\
                .strftime("%d.%m.%Y %H:%M")


app.jinja_env.filters["localtime"] = localtime