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


# TODO: Create a LoginForm to login existing users
# WTForm for registering a new user
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    pwd = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

# TODO: Create a CommentForm so users can leave comments below posts
