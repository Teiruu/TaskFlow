from flask import Flask, render_template, redirect, request, flash, url_for, session, logging, abort
from flask_session import Session
from model.db import db
from taskflow.model.user import Register, User, LoginForm, TodoForm, Todo
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
    if session.get("username"):
        return redirect("/dashboard")
    return render_template('base.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if session.get("username"):
        return redirect("/dashboard")
    form = Register()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
        )
        user.set_password(form.password.data)
        #Adds user to the DB
        db.session.add(user)
        db.session.commit()
        session["username"] = request.form.get("username")
        return redirect(url_for('dashboard'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get("username"):
        return redirect("/dashboard")
    form = LoginForm()
    if form.validate_on_submit():
        session["username"] = request.form.get("username")
        return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route("/logout", methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('base'))

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if not session.get("username"):
        return redirect("/login")
    form = TodoForm()
    user = db.session.execute(db.select(User).filter_by(username=session.get("username"))).scalar_one()
    if form.validate_on_submit():
        todo = Todo(
        user_id = user.id,
        todo_text = form.todo.data,
        todo_priority = form.priority.data,
        todo_date = form.date.data,
        completed = False
        )
    #Adding the task to the list
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('dashboard'))
    todos = db.session.execute(db.select(Todo).filter_by(user_id=user.id).order_by(Todo.todo_date)).scalars()
    return render_template('dashboard.html', form=form, todos=todos)

# Update task status
@app.route("/dashboard/update/<int:id>", methods=["POST"])
def update(id):
    todo = db.session.execute(db.select(Todo).filter_by(id=id)).scalar_one()
    user = db.session.execute(db.select(User).filter_by(username=session.get("username"))).scalar_one()
    if todo.user_id != user.id:
        abort(403)
    todo.completed = not todo.completed

    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route("/dashboard/delete/<int:id>", methods=["POST"])
def delete(id):
    task = db.session.execute(db.select(Todo).filter_by(id=id)).scalar_one()
    user = db.session.execute(db.select(User).filter_by(username=session.get("username"))).scalar_one()
    if task.user_id != user.id:
        abort(403)

    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('dashboard'))
