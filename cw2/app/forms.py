from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, PasswordField, SubmitField
from wtforms.widgets import HiddenInput
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from app.models import User, Tag

class RegistrationForm(FlaskForm):
    """Registration form"""
    username = StringField('Username', validators=[
        DataRequired('Please enter a username'),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired('Please enter an email address'),
        Email('Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired('Please enter a password'),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired('Please confirm your password'),
        EqualTo('password', message='Passwords do not match')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already taken. Please choose another.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered. Please use another email.')


class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username or Email', validators=[DataRequired('Please enter username or email')])
    password = PasswordField('Password', validators=[DataRequired('Please enter password')])
    remember_me = SelectField('Remember Me', choices=[('0', 'No'), ('1', 'Yes')], default='0')
    submit = SubmitField('Login')


class PostForm(FlaskForm):
    """Post form"""
    title = StringField('Title', validators=[
        DataRequired('Please enter a title'),
        Length(max=100, message='Title cannot exceed 100 characters')
    ])
    content = TextAreaField('Content', validators=[
        DataRequired('Please enter content'),
        Length(max=10000, message='Content cannot exceed 10000 characters')
    ])
    category = SelectField('Category', choices=[
        ('Technique', 'Technique'),
        ('Equipment', 'Equipment'),
        ('Tournament', 'Tournament'),
        ('Training', 'Training'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    tags = StringField('Tags', validators=[Length(max=200)])
    submit = SubmitField('Publish')
    save_draft = SubmitField('Save Draft')


class CommentForm(FlaskForm):
    """Comment form"""
    content = TextAreaField('Comment', validators=[
        DataRequired('Please enter a comment'),
        Length(max=2000, message='Comment cannot exceed 2000 characters')
    ])
    parent_id = StringField('Parent Comment ID', default='', widget=HiddenInput())
    submit = SubmitField('Post Comment')


class UserSettingsForm(FlaskForm):
    """User settings form"""
    username = StringField('Username', validators=[
        DataRequired('Please enter a username'),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired('Please enter an email address'),
        Email('Please enter a valid email address')
    ])
    bio = TextAreaField('Bio', validators=[
        Length(max=500, message='Bio cannot exceed 500 characters')
    ])
    avatar = FileField('Avatar', validators=[
        Optional()
        # Note: FileAllowed validator removed, file validation handled manually in routes
    ])
    submit = SubmitField('Save Changes')


class PasswordChangeForm(FlaskForm):
    """Password change form"""
    old_password = PasswordField('Current Password', validators=[DataRequired('Please enter current password')])
    new_password = PasswordField('New Password', validators=[
        DataRequired('Please enter new password'),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    new_password2 = PasswordField('Confirm New Password', validators=[
        DataRequired('Please confirm new password'),
        EqualTo('new_password', message='Passwords do not match')
    ])
    submit = SubmitField('Change Password')


