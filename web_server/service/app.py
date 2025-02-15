from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    send_file,
    session,
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from functools import wraps
import requests
import sqlite3
import os
import hashlib
import pickle
import re
import random
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32)
app.config["RECAPTCHA_SITE_KEY"] = "6LfzG5IbAAAAAEJu8NhVd4pksxsvDbIESbv7WKR_"
app.config["RECAPTCHA_SECRET_KEY"] = "6LfzG5IbAAAAAIKmnwglNzRzCVExZVTqWPKBKjwH"
app.config["UPLOAD_FOLDER"] = "/tmp/fact_app/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

blacklist = ["union", "select", "insert", "delete", "update", "UNION", "SELECT", "INSERT", "DELETE", "UPDATE", "offset", "OFFSET", "limit", "LIMIT", "="]


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

API_KEY_FILE = "/apikey.txt"
try:
    with open(API_KEY_FILE, "r") as f:
        API_KEY = f.read().strip()
except FileNotFoundError:
    print(f"Warning: API key file not found at {API_KEY_FILE}")
    API_KEY = None
except IOError:
    print(f"Error: Unable to read API key file at {API_KEY_FILE}")
    API_KEY = None


class User(UserMixin):
    def __init__(self, id, username, email, role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role


def verify_recaptcha(recaptcha_response):
    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        "secret": app.config["RECAPTCHA_SECRET_KEY"],
        "response": recaptcha_response,
    }
    response = requests.post(verify_url, data=data)
    result = response.json()
    return result.get("success", False)


@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user["id"], user["username"], user["email"], user["role"])
    return None


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


def simulate_delay(email):
    # Basic check to identify suspicious patterns
    delay = 0.1  # Base delay

    # Adjust the delay based on input characteristics
    if re.search(r"union|select|insert|delete|update|UNION|SELECT|INSERT|DELETE|UPDATE", email, re.IGNORECASE):
        delay += random.uniform(1.0, 3.0)  # Longer delay for suspicious inputs

    time.sleep(delay)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        recaptcha_response = request.form.get("g-recaptcha-response")
        if not verify_recaptcha(recaptcha_response):
            flash("Please complete the reCAPTCHA.", "error")
            return render_template(
                "login.html", recaptcha_site_key=app.config["RECAPTCHA_SITE_KEY"]
            )

        for i in blacklist:
            if re.search(i, email) or re.search(i, password):
                # Debugging
                print(f"DEBUG: Email '{email}' matched blacklist pattern: {i}") 
                simulate_delay(email) 
                flash(f"Invalid input, please try again!", "error")
                return render_template(
                    "login.html", recaptcha_site_key=app.config["RECAPTCHA_SITE_KEY"]
                )
        conn = get_db_connection()
        try:
            query = f"SELECT id, username, email, role FROM users WHERE email = '{email}' AND password = '{password}'"

            # Debugging
            print(f"Executing query: {query}")

            simulate_delay(email)
            record = conn.execute(query).fetchone()

            conn.close()
        except sqlite3.OperationalError as e:
            flash(e, "error")
            return render_template(
                "login.html", recaptcha_site_key=app.config["RECAPTCHA_SITE_KEY"]
            )

        if record:
            user_obj = User(
                record["id"], record["username"], record["email"], record["role"]
            )
            login_user(user_obj)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials, please try again!", "error")
            return render_template(
                "login.html", recaptcha_site_key=app.config["RECAPTCHA_SITE_KEY"]
            )

    return render_template(
        "login.html", recaptcha_site_key=app.config["RECAPTCHA_SITE_KEY"]
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        recaptcha_response = request.form.get("g-recaptcha-response")
        if not verify_recaptcha(recaptcha_response):
            flash("Please complete the reCAPTCHA.", "error")
            return render_template(
                "register.html", recaptcha_site_key=app.config["RECAPTCHA_SITE_KEY"]
            )

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template(
                "register.html", recaptcha_site_key=app.config["RECAPTCHA_SITE_KEY"]
            )

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?", (username, email)
        ).fetchone()

        if user:
            flash("Username or email already exists", "error")
            return render_template(
                "register.html", recaptcha_site_key=app.config["RECAPTCHA_SITE_KEY"]
            )

        conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password),
        )
        conn.commit()
        conn.close()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template(
        "register.html", recaptcha_site_key=app.config["RECAPTCHA_SITE_KEY"]
    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)


def length_filter(s):
    return len(s)


app.jinja_env.filters["length"] = length_filter


@app.route("/edit_profile")
@login_required
def edit_profile():
    # Simulate an error when the user tries to edit the profile
    db_name = "users"  # This is the name of your SQLite database
    error_message = (
        f"An error occurred while trying to access the profile from {db_name}"
    )
    abort(500, description=error_message)


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error.html", error_message=e.description), 500


@app.route("/dashboard")
@login_required
def dashboard():
    fact = get_random_fact()
    days_active = 30
    facts_learned = 15
    newly_uploaded_facts = session.pop("newly_uploaded_facts", [])
    return render_template(
        "dashboard.html",
        fact=fact["content"] if fact else None,
        fact_id=fact["id"] if fact else None,
        days_active=days_active,
        facts_learned=facts_learned,
        newly_uploaded_facts=newly_uploaded_facts,
    )


def get_random_fact():
    conn = get_db_connection()
    fact = conn.execute(
        "SELECT id, content FROM facts ORDER BY RANDOM() LIMIT 1"
    ).fetchone()
    conn.close()
    return fact if fact else None


@app.route("/get_new_fact")
@login_required
def get_new_fact():
    fact = get_random_fact()
    return {
        "fact": fact["content"] if fact else None,
        "fact_id": fact["id"] if fact else None,
    }


@app.route("/download_fact")
@login_required
def download_fact():
    args = request.args
    fact_id = args.get("id")
    print(fact_id)
    if not fact_id:
        flash("No fact ID provided.", "error")
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    fact = conn.execute("SELECT content FROM facts WHERE id = ?", (fact_id,)).fetchone()
    conn.close()

    fact_file_path = os.path.join("/tmp/fact_app/downloads/", fact_id)
    print(fact_file_path)
    if fact:
        fact_content = fact["content"]

        # Ensure the directory exists
        os.makedirs(os.path.dirname(fact_file_path), exist_ok=True)

        # Write the fact to the file
        with open(fact_file_path, "w") as f:
            f.write(fact_content)

    # Read the file and send it
    return send_file(
        fact_file_path,
        mimetype="text/plain",
        as_attachment=True,
        download_name=f"fact_{fact_id}.txt",
    )


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() == "pkl"


@app.route("/upload_facts", methods=["POST"])
@login_required
@admin_required
def upload_facts():
    if not API_KEY:
        flash("Server configuration error: API key not available", "error")
        return redirect(url_for("dashboard"))

    if "facts_file" not in request.files:
        flash("No file part", "error")
        return redirect(url_for("dashboard"))

    file = request.files["facts_file"]
    api_key = request.form.get("api_key")

    if file.filename == "":
        flash("No selected file", "error")
        return redirect(url_for("dashboard"))

    if api_key != API_KEY:
        flash("Invalid API key", "error")
        return redirect(url_for("dashboard"))

    if file and allowed_file(file.filename):
        filename = hashlib.md5(file.filename.encode()).hexdigest() + ".pkl"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        try:
            with open(filepath, "rb") as f:
                facts = pickle.load(f)

            if not isinstance(facts, list):
                raise ValueError("Uploaded file does not contain a list of facts")

            conn = get_db_connection()
            newly_uploaded_facts = []
            for fact in facts:
                if isinstance(fact, str) and fact.strip():
                    conn.execute("INSERT INTO facts (content) VALUES (?)", (fact,))
                    newly_uploaded_facts.append(fact)
            conn.commit()
            conn.close()

            flash(
                f"{len(newly_uploaded_facts)} facts have been uploaded successfully!",
                "success",
            )
            session["newly_uploaded_facts"] = newly_uploaded_facts
        except Exception as e:
            flash(f"Error processing file: {str(e)}", "error")
        finally:
            os.remove(filepath)
    else:
        flash("Invalid file type. Please upload a .pkl file.", "error")

    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
