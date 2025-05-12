from flask import Flask, render_template, redirect, request, flash, url_for, session, logging
from flask_session import Session
from model.db import db
from taskflow.model.user import Register, User, LoginForm
from flask_login import LoginManager

app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)
app.config.from_pyfile('instance/config.py')
with app.app_context():
    db.create_all()
#Login session config/initialize
app.config["SESSION_PERMANENT"] = False     # Sessions expire when the browser is closed
app.config["SESSION_TYPE"] = "filesystem"     # Store session data in files

# Initialize Flask-Session
Session(app)


@app.route("/")
def base():
    return render_template('base.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = Register()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            password=form.password.data
        )
        #Adds user to the DB
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session["username"] = request.form.get("username")
        return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route("/logout", methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('base'))

@app.route("/dashboard")
def dashboard():
    if not session.get("username"):
        return redirect("/login")
    return render_template('dashboard.html')

