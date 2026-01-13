from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect("database.db")

def init_db():
    db = get_db()
    cur = db.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        bio TEXT,
        links TEXT,
        music TEXT
    )
    """)
    db.commit()
    db.close()

# ---------- ROUTES ----------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pw = request.form["password"]

        db = get_db()
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (user, pw)
        )
        result = cur.fetchone()

        if result:
            session["user"] = user
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO users VALUES (?,?,?,?,?)",
            (
                request.form["username"],
                request.form["password"],
                "",
                "",
                ""
            )
        )
        db.commit()
        return redirect("/")
    return render_template("register.html")

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    if request.method == "POST":
        cur.execute("""
        UPDATE users SET bio=?, links=?, music=?
        WHERE username=?
        """,(
            request.form.get("bio", ""),
            request.form.get("links", ""),
            request.form.get("music", ""),
            session["user"]
        ))
        db.commit()

    cur.execute("SELECT * FROM users WHERE username=?", (session["user"],))
    user = cur.fetchone()
    return render_template("dashboard.html", user=user)

@app.route("/<username>")
def profile(username):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cur.fetchone()
    if not user:
        return "User not found"
    return render_template("profile.html", user=user)

# ---------- START ----------
init_db()  # <<< YE SABSE IMPORTANT LINE

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port, debug=True)
