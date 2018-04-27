from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, SelectField,PasswordField
from wtforms.validators import InputRequired, DataRequired, Email
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask import Flask, render_template, flash, session, redirect, url_for

class UploadForm(FlaskForm):
    caption = TextAreaField('Description', validators=[InputRequired(message='Description is required')])
    upload = FileField('Image', validators=[FileRequired('Please input a file'), FileAllowed(['jpg', 'png'], 'Images only!')])

 
class PostForm(FlaskForm):
    upload = FileField('Picture', validators=[FileRequired("Please input file"),FileAllowed(['jpg','png','jpeg'], 'Only jpg,jpeg and png images can be uploaded!')])
    caption = TextAreaField('Caption', validators = [DataRequired("Caption is required")])    
    
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired('Username is required')])
    password = PasswordField('Password', validators=[DataRequired('Password is required')])
    firstname = StringField('Firstname', validators=[DataRequired('Firstname is required')])
    lastname = StringField('Lastname', validators=[DataRequired('Lastname is required')])
    email = StringField('email', validators = [DataRequired("Your email is required"), Email("Email only!")])
    location = StringField('Location', validators=[DataRequired('Location is required')])
    biography = TextAreaField('Biography', validators = [DataRequired("Biography is required")])
    upload = FileField('images', validators=[FileRequired("Please input file"),FileAllowed(['jpg','png','jpeg'], 'Only jpg,jpeg and png images can be uploaded!')])
    button = SubmitField('Register')
    
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired('Username is required')])
    password = PasswordField('Password', validators=[DataRequired('Password is required')])
    

    