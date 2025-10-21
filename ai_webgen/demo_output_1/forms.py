from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SelectField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    """Registration form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])


class TaskForm(FlaskForm):
    """Task creation form"""
    title = StringField('Task Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description')
    status = SelectField('Status', choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')])
    priority = SelectField('Priority', choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')])

class ProjectForm(FlaskForm):
    """Project form"""
    name = StringField('Project Name', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description')

