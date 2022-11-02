import os
import re
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask_mail import *
from random import *
from helpers import login_required

# Configure application
app = Flask(__name__)

app.secret_key = 'your secret key'

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

mail = Mail(app)
app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
otp = randint(000000,999999)

db = SQL("sqlite:///final.db")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Ensure user enters via POST
    if request.method == "POST":

        # Get name
        name = request.form.get("username")
        email = request.form.get("email")
        # Get username check to know if name already exist
        usernameCheck = db.execute("SELECT username FROM users WHERE username = ?", request.form.get("username"))

        if not request.form.get("firstname"):
            flash("Enter your First name")
            return render_template("register.html")

        elif not request.form.get("lastname"):
            flash("Enter your Last name")
            return render_template("register.html")
        # Ensure username was submitted
        elif not request.form.get("username"):
            flash("Must enter username")
            return render_template("register.html")
        elif not email:
            flash("Must enter an email")
            return render_template("register.html")

        elif not (re.fullmatch(regex, email)):
            flash("Invalid email")
            return render_template("register.html")

        # Else if username already exists
        elif usernameCheck:
            flash("Username already exists")
            return render_template("register.html")

        # Else if password was not submitted
        elif not request.form.get("password"):
            flash("Must provide a password")
            return render_template("register.html")

        # Else if confirmation was not submitted
        elif not request.form.get("confirmation"):
            flash("Must confirm Password")
            return render_template("register.html")

        # Else if password is not the same
        elif request.form.get("password") != request.form.get("confirmation"):
            flash("Password must match")
            return render_template("register.html")

        # Hash password
        password = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

        # Insert user into table
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        message = Message('OTP',sender = 'PyBiz', recipients = [email])
        message.body = str(otp)
        mail.send(message)
        flash("Registration successful!")
        db.execute("INSERT INTO users (email, firstname, lastname, username, hash) VALUES(?,?,?,?,?)", email, request.form.get("firstname"), request.form.get("lastname"), name, password)
        return render_template("verify.html")
    # If user enters via GET
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        name = request.form.get("username")
        if not request.form.get("username"):
            flash("Must provide username")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Welcome! Log in successful")
        redir = db.execute("SELECT * FROM survey WHERE id = ?", session["user_id"])
        if len(redir) != 0:
            return redirect("/")
        else:
            return render_template("main.html")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route('/validate',methods=["POST"])
def validate():
    user_otp = request.form['otp']
    if otp == int(user_otp):
        return render_template("redirect.html")
    else:
        return render_template("failure.html")
    if __name__ == '__main__':
        app.config['SESSION_TYPE'] = 'filesystem'

        sess.init_app(app)
        app.run(debug = True)
@app.route("/success")
@login_required
def success():
    return render_template("success.html")

@app.route("/verify")
def verify():
    return render_template("verify.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/main", methods=["GET", "POST"])
@login_required
def main():
    if request.method == "POST":
        email = request.form.get("email")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        username = request.form.get("username")
        course = request.form.get("course")
        phone = request.form.get("phone")
        user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
        if not email:
            flash("Enter an email")
            return render_template("main.html")

        elif not (re.fullmatch(regex, email)):
            flash("Enter a valid email")
            return render_template("main.html")

        elif not firstname:
            flash("Please enter your First name")
            return render_template("main.html")

        elif not lastname:
            flash("Please enter your Last name")
            return render_template("main.html")

        elif not username:
            flash("Please enter your username, same you used to register")
            return render_template("main.html")

        elif not username != user:
            flash("Please the same username you used to register!")
            return render_template("main.html")

        elif not phone:
            flash("Please enter your Phone number")
            return render_template("main.html")

        elif not course:
            flash("Choose a course")
            return render_template("main.html")

        db.execute("INSERT INTO survey VALUES(?,?,?,?,?,?,?)", session["user_id"], email, firstname, lastname, course, phone, username)

        if course == "Beginner":
            return render_template("beginner.html")

        elif course =="Web Development":
            return render_template("unavailable.html")

        elif course =="Data Visualisation":
            return render_template("unavailable.html")

        elif course =="Data Analytics":
            return render_template("unavailable.html")

        elif course =="AI and Machine Learning":
            return render_template("unavailable.html")

        elif course =="Programming Applications":
            return render_template("unavailable.html")

        elif course =="Game Development":
            return render_template("unavailable.html")

        elif course =="Language Development":
            return render_template("unavailable.html")

        elif course =="Finance":
            return render_template("unavailable.html")

        elif course =="SEO":
            return render_template("unavailable.html")

        elif course =="Design":
            return render_template("unavailable.html")

    return render_template("main.html")


@app.route("/course")
def co():
    course = db.execute("SELECT course FROM survey WHERE id = ?", session["user_id"])
    course = course[0]["course"]
    if course == "Beginner":
        return render_template("beginner.html")

    elif course =="Web Development":
        return render_template("unavailable.html")

    elif course =="Data Visualisation":
        return render_template("unavailable.html")

    elif course =="Data Analytics":
        return render_template("unavailable.html")

    elif course =="AI and Machine Learning":
        return render_template("unavailable.html")

    elif course =="Programming Applications":
        return render_template("unavailable.html")

    elif course =="Game Development":
        return render_template("unavailable.html")

    elif course =="Language Development":
        return render_template("unavailable.html")

    elif course =="Finance":
        return render_template("unavailable.html")

    elif course =="SEO":
        return render_template("unavailable.html")

    elif course =="Design":
        return render_template("unavailable.html")


@app.route("/hello")
def hello():
    return render_template("hello.html")


@app.route("/beginner")
def beginner():
    return render_template("beginner.html")


@app.route("/very", methods=["GET","POST"])
def verif():
    if request.method == "POST":
        answer = request.form.get("answer")
        if not answer:
            flash("Enter a valid answer")
            return render_template("hello.html")

        elif "print" not in answer and "\"" not in answer and "\"" not in answer and "(" not in answer and ")" not in answer:
            flash("Incorrect answer, Try to compile your answer and try again")
            return render_template("hello.html")

        else:
            track = "Lesson1"
            db.execute("INSERT INTO progress VALUES(?,?)", session["user_id"],track )
            return render_template("beginner.html", message ="Lesson 1 completed! Nice job, move on to the next task")

    else:
        return render_template("hello.html")


@app.route("/prin")
def prin():
    return render_template("print.html")


@app.route("/prinquiz")
def quiz():
    return render_template("prinquiz.html")


@app.route("/squiz", methods=["GET", "POST"])
def squiz():
    if request.method == "POST":
        ans1 = request.form.get("answer")
        ans2 = request.form.get("quiz")

        if not ans1:
            return render_template("prinquiz.html", msg="Enter your answer")
        elif ans1 != "\\n":
            return render_template("prinquiz.html", msg = "Incorrect, try again")
        elif not ans2:
            return render_template("prinquiz.html", msg="Choose an answer")
        elif ans2 != "end":
            return render_template("prinquiz.html", msg="Incorrect choice, try again")
        else:
            track = "Lesson2"
            db.execute("UPDATE progress SET prog = ? WHERE id = ?",track, session["user_id"])
            return render_template("beginner.html", message="Lesson 2 completed! Move on to the final task")
    return render_template("prinquiz.html")


@app.route("/variables")
def variables():
    return render_template("variables.html")


@app.route("/editor")
def editor():
    return render_template("editor.html")


@app.route("/finaltest")
def last():
    return render_template("finaltest.html")


@app.route("/finale", methods=["GET", "POST"])
def finale():
    if request.method == "POST":
        first = request.form.get("quiz")
        second = request.form.get("del")
        third = request.form.get("comm")
        if not first:
            return render_template("finaltest.html", message="Choose an option")
        elif first != "right":
            return render_template("finaltest.html", message="Incorrect answer, try again!")
        elif not second:
            return render_template("finaltest.html", message="Enter an anwer")
        elif second != "del":
            return render_template("finaltest.html", message="Incorrect answer, try again!")
        elif not third:
            return render_template("finaltest.html", message="Choose an option")
        elif third != "right":
            return render_template("finaltest.html", message="Incorrect answer, try again!")
        else:
            track = "Lesson3"
            db.execute("UPDATE progress SET prog = ? WHERE id = ?",track, session["user_id"])
            return render_template("beginner.html", message="Congratulations, all lessons completed")
    else:
        return render_template("finaltest.html")


@app.route("/progress")
def progress():
    progress = db.execute("SELECT * from progress WHERE id=?", session["user_id"])
    if len(progress) != 0:
        progress = progress[0]["prog"]
        if progress == "Lesson1":
            track = 33.3
        elif progress == "Lesson2":
            track = 66.6
        elif progress == "Lesson3":
            track = 100
    else:
        track = 0
    return render_template("progress.html", track=track)


@app.route("/unavailable")
def un():
    return render_template("unavailable.html")
