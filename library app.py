from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret123"

# Dummy users
users = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"}
}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username]["password"] == password:
             session["user"] = username
             session["role"] = users[username]["role"]
             role = users[username]["role"]
             if role == "admin":
                 return redirect(url_for("admin_home"))
             else:
                 return redirect(url_for("user_home"))
        else:
            return "Invalid Credentials"

    return render_template("login.html")


@app.route("/admin")
def admin_home():
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    return render_template("admin_home.html", books=books)

@app.route("/user")
def user_home():
    if "user" not in session:
        return redirect(url_for("login"))

    return "<h2>Welcome User</h2>"

@app.route("/transactions")
def transactions():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("transactions.html")

@app.route("/maintenance")
def maintenance():
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    return render_template("maintenance.html")

# Temporary storage (in memory)
books = []

@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    if request.method == "POST":
        books.append({
            "type": request.form["type"],
            "book_name": request.form["name"],
            "author": request.form["author"],
            "date": request.form["date"],
            "qty": request.form["qty"],
            "category": "General"
        })

        return redirect(url_for("success"))

    return render_template("add_book.html")

@app.route("/update_book", methods=["GET", "POST"])
def update_book():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]

        for b in books:
            if b["book_name"] == name:

                if request.form.get("type"):
                    b["type"] = request.form["type"]

                if request.form.get("date"):
                    b["date"] = request.form["date"]

                if request.form.get("status"):
                    b["status"] = request.form["status"]

        return redirect(url_for("success"))

    return render_template("update_book.html")

@app.route("/view_books")
def view_books():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("view_books.html", books=books)

issued_books = []

from datetime import datetime, timedelta

@app.route("/issue_book", methods=["GET", "POST"])
def issue_book():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        book_name = request.form["book_name"]
        author = request.form["author"]
        issue_date = request.form["issue_date"]

        # auto return date (15 days)
        issue_dt = datetime.strptime(issue_date, "%Y-%m-%d")
        return_dt = issue_dt + timedelta(days=15)

        issued_books.append({
            "book_name": book_name,
            "author": author,
            "issue_date": issue_date,
            "return_date": return_dt.strftime("%Y-%m-%d"),
            "returned": False
        })

        return redirect(url_for("success"))

    return render_template("issue_book.html", books=books)

@app.route("/return_book", methods=["GET", "POST"])
def return_book():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        book_name = request.form["book_name"]

        for b in issued_books:
            if b["book_name"] == book_name and not b["returned"]:
                b["returned"] = True

                # check overdue
                today = datetime.today()
                return_dt = datetime.strptime(b["return_date"], "%Y-%m-%d")

                if today > return_dt:
                    fine = (today - return_dt).days * 10
                    return redirect(url_for("pay_fine", fine=fine))
                else:
                    return redirect(url_for("success"))

    return render_template("return_book.html", books=books)

@app.route("/reports")
def reports():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("reports.html")

@app.route("/book_available", methods=["GET", "POST"])
def book_available():
    if "user" not in session:
        return redirect(url_for("login"))

    results = []
    result = None

    if request.method == "POST":
        book_name = request.form["book_name"]
        author = request.form["author"]

        for book in books:
            if (book_name.lower() in book["book_name"].lower()) or \
               (author.lower() in book["author"].lower()):
                results.append(book)

        if not results:
            result = "No books found"

    return render_template("book_available.html", results=results, result=result)

@app.route("/pay_fine", methods=["GET", "POST"])
def pay_fine():
    if "user" not in session:
        return redirect(url_for("login"))

    fine = int(request.args.get("fine", 0))

    if request.method == "POST":
        if fine > 0 and "paid" not in request.form:
            return "Please pay fine before submitting"

        return redirect(url_for("admin_home"))

    return render_template("pay_fine.html", fine=fine)

@app.route("/master_books")
def master_books():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("master_books.html", books=books)

@app.route("/master_movies")
def master_movies():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("master_movies.html", books=books)

@app.route("/master_memberships")
def master_memberships():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("master_memberships.html", memberships=memberships)

memberships = [
    {
        "id": "M001",
        "name": "John",
        "phone": "1234567890",
        "address": "Hyderabad",
        "aadhar": "1234-5678-9012",
        "start": "2024-01-01",
        "end": "2025-01-01",
        "status": "Active",
        "fine": 0
    }
]
@app.route("/active_issues")
def active_issues():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("active_issues.html", issued_books=issued_books)

from datetime import datetime

@app.route("/overdue_returns")
def overdue_returns():
    if "user" not in session:
        return redirect(url_for("login"))

    today = datetime.today().strftime("%Y-%m-%d")
    today_dt = datetime.today()

    # convert return_date string → datetime
    for b in issued_books:
        b["return_dt"] = datetime.strptime(b["return_date"], "%Y-%m-%d")

    return render_template(
        "overdue_returns.html",
        issued_books=issued_books,
        today=today,
        today_dt=today_dt
    )

@app.route("/issue_requests")
def issue_requests():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("issue_requests.html", issued_books=issued_books)

memberships = []

@app.route("/add_membership", methods=["GET", "POST"])
def add_membership():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        memberships.append({
            "id": f"M{len(memberships)+1}",
            "name": request.form["first_name"] + " " + request.form["last_name"],
            "phone": request.form["contact"],
            "address": request.form["address"],
            "aadhar": request.form["aadhar"],
            "start": request.form["start_date"],
            "end": request.form["end_date"],
            "status": "Active",
            "fine": 0
        })

        return redirect(url_for("success"))

    return render_template("add_membership.html")

@app.route("/update_membership", methods=["GET", "POST"])
def update_membership():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        mid = request.form["id"]

        for m in memberships:
            if m["id"] == mid:

                # Update dates
                if request.form.get("start_date"):
                    m["start"] = request.form["start_date"]

                if request.form.get("end_date"):
                    m["end"] = request.form["end_date"]

                # Remove membership
                if "remove" in request.form:
                    m["status"] = "Inactive"

        return redirect(url_for("success"))

    return render_template("update_membership.html")

users_list = []

@app.route("/user_management", methods=["GET", "POST"])
def user_management():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        users_list.append({
            "name": request.form["name"],
            "active": "active" in request.form,
            "admin": "admin" in request.form
        })

        return redirect(url_for("success"))

    return render_template("user_management.html")

@app.route("/cancel")
def cancel():
    return render_template("cancel.html")

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/logout")
def logout():
    session.clear()   # 🔥 important
    return render_template("logout.html")

if __name__ == "__main__":
    app.run(debug=True)