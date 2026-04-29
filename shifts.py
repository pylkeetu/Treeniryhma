import db


def get_all():
    return db.query("SELECT * FROM shifts")


def get_shift(item_id):
    shift = db.query(
        """SELECT shifts.*, employees.username
           FROM shifts
           JOIN employees ON shifts.employee_id = employees.id
           WHERE shifts.id = ?""",
        [item_id]
    )

    if not shift:
        return None

    categories = db.query(
        """SELECT categories.name
           FROM categories
           JOIN shift_categories ON categories.id = shift_categories.category_id
           WHERE shift_categories.shift_id = ?""",
        [item_id]
    )

    comments = db.query(
        """SELECT comments.*, employees.username
           FROM comments
           JOIN employees ON comments.employee_id = employees.id
           WHERE comments.shift_id = ?
           ORDER BY comments.created_at DESC""",
        [item_id]
    )

    return {
        "shift": shift[0],
        "categories": categories,
        "comments": comments
    }


def get_categories():
    return db.query("SELECT * FROM categories")


def create(employee_id):
    description = request.form["description"]
    participants = request.form["participants"]
    category_id = request.form["category"]

    if not category_id:
        abort(403)

    cat = db.query("SELECT name FROM categories WHERE id = ?", [category_id])
    if not cat:
        abort(403)

    title = cat[0]["name"]

    shift_id = db.execute(
        """INSERT INTO shifts (title, description, participants, employee_id)
           VALUES (?, ?, ?, ?)""",
        [title, description, participants, employee_id]
    )

    db.execute(
        "INSERT INTO shift_categories (shift_id, category_id) VALUES (?, ?)",
        [shift_id, category_id]
    )

    return redirect("/")


def edit_form(item_id, employee_id):
    shift = db.query("SELECT * FROM shifts WHERE id = ?", [item_id])

    if not shift or shift[0]["employee_id"] != employee_id:
        return None

    return {
        "shift": shift[0],
        "categories": get_categories()
    }


def update(item_id, employee_id):
    shift = db.query("SELECT employee_id FROM shifts WHERE id = ?", [item_id])

    if not shift or shift[0]["employee_id"] != employee_id:
        abort(403)

    description = request.form["description"]
    participants = request.form["participants"]
    category_id = request.form["category"]

    cat = db.query("SELECT name FROM categories WHERE id = ?", [category_id])
    title = cat[0]["name"]

    db.execute(
        """UPDATE shifts
           SET title = ?, description = ?, participants = ?
           WHERE id = ?""",
        [title, description, participants, item_id]
    )

    return redirect(f"/shift/{item_id}")


def delete(item_id, employee_id):
    shift = db.query("SELECT employee_id FROM shifts WHERE id = ?", [item_id])

    if not shift or shift[0]["employee_id"] != employee_id:
        abort(403)

    db.execute("DELETE FROM shift_categories WHERE shift_id = ?", [item_id])
    db.execute("DELETE FROM shifts WHERE id = ?", [item_id])

    return redirect("/")


def add_comment(shift_id, employee_id):
    content = request.form["content"]

    if len(content) > 100:
        abort(403)

    db.execute(
        "INSERT INTO comments (content, employee_id, shift_id) VALUES (?, ?, ?)",
        [content, employee_id, shift_id]
    )

    return redirect(f"/shift/{shift_id}")