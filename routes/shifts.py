from flask import Blueprint, render_template, request, redirect, session, flash
import db

shifts_bp = Blueprint("shifts", __name__)

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

    return render_template("index.html", shifts=all_shifts)

@shifts_bp.route("/shift/<int:item_id>")
def show_shift(item_id):

    result = db.query("""
        SELECT shifts.*, employees.username
        FROM shifts
        JOIN employees ON shifts.employee_id = employees.id
        WHERE shifts.id = ?
    """, [item_id])

    if not result:
        return "Ei löydy", 404

    return render_template("show_shift.html", shift=result[0])

@shifts_bp.route("/new_shift")
def new_shift():
    categories = db.query("SELECT * FROM categories")
    return render_template("new_shift.html", categories=categories)


@shifts_bp.route("/create_shift", methods=["POST"])
def create_shift():

    if "employee_id" not in session:
        return redirect("/login")

    description = request.form["description"]
    participants = request.form["participants"]
    employee_id = session["employee_id"]
    category_id = request.form["category"]

    cat = db.query(
        "SELECT name FROM categories WHERE id = ?",
        [category_id]
    )

    if not cat:
        return "Kategoria ei löydy", 400

    title = cat[0]["name"]

    shift_id = db.execute(
        "INSERT INTO shifts (title, description, participants, employee_id) VALUES (?, ?, ?, ?)",
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

    return render_template("edit_shift.html", shift=shift)

@shifts_bp.route("/shift/<int:item_id>/edit", methods=["POST"])
def edit(item_id):
    result = db.query("SELECT employee_id FROM shifts WHERE id = ?", [item_id])

    if result[0][0] != session["employee_id"]:
        return "Ei oikeuksia", 403

    db.execute(
        "UPDATE shifts SET title = ?, description = ?, participants = ? WHERE id = ?",
        [request.form["title"], request.form["description"], request.form["participants"], item_id]
    )

    return redirect(f"/shift/{item_id}")

@shifts_bp.route("/shift/<int:item_id>/delete", methods=["POST"])
def delete(item_id):

    if "employee_id" not in session:
        return redirect("/login")

    result = db.query("SELECT employee_id FROM shifts WHERE id = ?", [item_id])

    if result[0][0] != session["employee_id"]:
        return "Ei oikeuksia", 403

    db.execute("DELETE FROM shifts WHERE id = ?", [item_id])
    return redirect("/")