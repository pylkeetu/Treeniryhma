from flask import Blueprint, render_template, request, redirect, session, flash
import db

shifts_bp = Blueprint("shifts", __name__)

def validate_shift(description, participants):
    if len(description) > 100:
        return "Kuvaus saa olla enintään 100 merkkiä"

    try:
        participants = int(participants)
    except ValueError:
        return "Osallistujien määrän pitää olla numero"

    if participants < 1:
        return "Osallistujia pitää olla vähintään 1"

    if participants > 100:
        return "Osallistujia voi olla enintään 100"

    return None

@shifts_bp.route("/")
def index():
    search = request.args.get("q")

    if search:
        all_shifts = db.query(
            "SELECT * FROM shifts WHERE title LIKE ? OR description LIKE ?",
            [f"%{search}%", f"%{search}%"]
        )

        if all_shifts:
            flash("Työvuoro löytyi", "success")
        else:
            flash("Työvuoroa ei löydetty", "error")
    else:
        all_shifts = db.query("SELECT * FROM shifts")
    
    users = db.query("SELECT id, username FROM employees")

    return render_template("index.html", shifts=all_shifts, users=users)

@shifts_bp.route("/shift/<int:item_id>")
def show_shift(item_id):

    shift = db.query("""
        SELECT shifts.*, employees.username
        FROM shifts
        JOIN employees ON shifts.employee_id = employees.id
        WHERE shifts.id = ?
    """, [item_id])

    if not shift:
        return "Ei löydy", 404

    shift = shift[0]

    categories = db.query("""
        SELECT categories.name
        FROM categories
        JOIN shift_categories ON categories.id = shift_categories.category_id
        WHERE shift_categories.shift_id = ?
    """, [item_id])

    comments = db.query("""
        SELECT comments.*, employees.username
        FROM comments
        JOIN employees ON comments.employee_id = employees.id
        WHERE comments.shift_id = ?
        ORDER BY comments.created_at DESC
    """, [item_id])

    return render_template("show_shift.html", shift=shift, categories=categories, comments=comments)

@shifts_bp.route("/new_shift")
def new_shift():
    categories = db.query("SELECT * FROM categories")
    return render_template("new_shift.html", categories=categories)


@shifts_bp.route("/create_shift", methods=["POST"])
def create_shift():

    if "employee_id" not in session:
        return redirect("/login")

    description = request.form.get("description", "").strip()
    participants = request.form.get("participants", "").strip()
    employee_id = session["employee_id"]

    category_id = request.form.get("category")

    error = validate_shift(description, participants)
    if error:
        flash(error, "error")
        return redirect("/new_shift")

    if not category_id:
        flash("Valitse kategoria", "error")
        return redirect("/new_shift")

    cat = db.query(
        "SELECT name FROM categories WHERE id = ?",
        [category_id]
    )

    if not cat:
        flash("Kategoria ei löydy", "error")
        return redirect("/new_shift")

    title = cat[0]["name"]

    shift_id = db.execute(
        """
        INSERT INTO shifts (title, description, participants, employee_id)
        VALUES (?, ?, ?, ?)
        """,
        [title, description, participants, employee_id]
    )

    db.execute(
        "INSERT INTO shift_categories (shift_id, category_id) VALUES (?, ?)",
        [shift_id, category_id]
    )

    return redirect("/")

@shifts_bp.route("/shift/<int:item_id>/edit", methods=["GET"])
def edit_form(item_id):

    if "employee_id" not in session:
        return redirect("/login")

    result = db.query("SELECT * FROM shifts WHERE id = ?", [item_id])

    if not result:
        return "Ei löydy", 404

    shift = result[0]

    if shift["employee_id"] != session["employee_id"]:
        return "Ei oikeuksia", 403

    categories = db.query("SELECT * FROM categories")

    return render_template("edit_shift.html", shift=shift, categories=categories)

@shifts_bp.route("/shift/<int:item_id>/edit", methods=["POST"])
def edit(item_id):

    result = db.query(
        "SELECT employee_id FROM shifts WHERE id = ?",
        [item_id]
    )

    if result[0][0] != session["employee_id"]:
        return "Ei oikeuksia", 403

    description = request.form.get("description", "")
    participants = request.form.get("participants", "")
    category_id = request.form.get("category")

    error = validate_shift(description, participants)
    if error:
        flash(error, "error")
        return redirect(f"/shift/{item_id}/edit")

    if not category_id:
        flash("Valitse kategoria", "error")
        return redirect(f"/shift/{item_id}/edit")

    cat = db.query(
        "SELECT name FROM categories WHERE id = ?",
        [category_id]
    )

    if not cat:
        flash("Kategoria ei löydy", "error")
        return redirect(f"/shift/{item_id}/edit")

    title = cat[0]["name"]

    db.execute(
        """
        UPDATE shifts
        SET title = ?, description = ?, participants = ?
        WHERE id = ?
        """,
        [title, description, participants, item_id]
    )

    return redirect(f"/shift/{item_id}")

@shifts_bp.route("/shift/<int:item_id>/delete", methods=["POST"])
def delete(item_id):

    if "employee_id" not in session:
        return redirect("/login")

    result = db.query("SELECT employee_id FROM shifts WHERE id = ?", [item_id])

    if not result:
        return "Ei löydy", 404

    if result[0][0] != session["employee_id"]:
        return "Ei oikeuksia", 403
    
    db.execute(
        "DELETE FROM shift_categories WHERE shift_id = ?",
        [item_id]
    )

    db.execute("DELETE FROM shifts WHERE id = ?", [item_id])

    return redirect("/")

@shifts_bp.route("/shift/<int:shift_id>/comment", methods=["POST"])
def add_comment(shift_id):

    if "employee_id" not in session:
        return redirect("/login")

    content = request.form["content"]
    employee_id = session["employee_id"]

    if len(content) > 100:
        flash("Kommentti saa olla enintään 100 merkkiä", "error")
        return redirect(f"/shift/{shift_id}")

    db.execute(
        "INSERT INTO comments (content, employee_id, shift_id) VALUES (?, ?, ?)",
        [content, employee_id, shift_id]
    )

    return redirect(f"/shift/{shift_id}")