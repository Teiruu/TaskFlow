import datetime

from typing import List
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from model.db import db
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.fields.datetime import DateField
from wtforms.widgets import PasswordInput
from wtforms.validators import DataRequired, ValidationError, InputRequired, Length, EqualTo

# Username and Password Checker
def invalid_credentials(form, field):
    username_entered = form.username.data
    password_entered = field.data
#Check if credentials are valid
    user = db.session.execute(db.select(User).filter_by(username=username_entered)).scalar_one_or_none()
    if user is None:
        raise ValidationError('Username or password is incorrect')
    elif password_entered != user.password:
        raise ValidationError('Username or password is incorrect')


# class for the database username
class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    todos: Mapped[List["Todo"]] = relationship()
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()

#class for the database to-do
class Todo(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    todo_text: Mapped[str] = mapped_column()
    todo_priority: Mapped[int] = mapped_column()
    todo_date: Mapped[datetime.datetime] = mapped_column()


# class for the register form
class Register(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', widget=PasswordInput(hide_value=False), validators=[DataRequired()])
    def validate_username(form, field):
        user = db.session.execute(db.select(User).filter_by(username=field.data)).scalar_one_or_none()
        if user is not None:
            raise ValidationError('Username already exists, try another.')

#class for the login
class LoginForm(FlaskForm):
    username = StringField('username_label',
                           validators=[InputRequired(message="Username required")])
    password = StringField('password_label',
                           validators=[InputRequired(message="Password required"), invalid_credentials])

#class for the todo form
class TodoForm(FlaskForm):
    todo = StringField('todo_label',
                           validators=[InputRequired(message="Input required")])
    priority = SelectField('priority_label',
                           choices=[(1, 'Top'), (2, 'Middle'), (3, 'Less')])
    date = DateField('date_label', format='%Y-%m-%d')