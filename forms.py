from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class SignupForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(1,120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    role = SelectField("Role", choices=[("student","Student"),("warden","Warden")])
    submit = SubmitField("Sign Up")

class RoomForm(FlaskForm):
    room_no = StringField("Room No", validators=[DataRequired(), Length(1,50)])
    capacity = IntegerField("Capacity", validators=[DataRequired(), NumberRange(min=1)])
    block = StringField("Block")
    submit = SubmitField("Save")

class ComplaintForm(FlaskForm):
    subject = StringField("Subject", validators=[DataRequired(), Length(1,200)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(1,2000)])
    submit = SubmitField("Submit")

class AllocateForm(FlaskForm):
    student_email = StringField("Student Email", validators=[DataRequired(), Email()])
    room_no = StringField("Room No", validators=[DataRequired()])
    submit = SubmitField("Allocate")
