from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# WTForm for registering a new user
class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    pwd = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


# WTForm for registering a new user
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    pwd = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class Comment(FlaskForm):
    comment = CKEditorField("Let us know what you think", validators=[DataRequired()])
    submit = SubmitField("Post comment")

