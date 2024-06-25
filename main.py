from datetime import date

import flask
from flask import Flask, abort, request, render_template, redirect, url_for, flash, g, session
from functools import wraps
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Text, ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from sqlalchemy.sql import exists
from typing import List

# TODO: Delete post error
# TODO: Check edit post if error

# Function to hash and salt a user's password
def hash_password(user_password):

    pwhash = generate_password_hash(
        password=user_password,
        method="pbkdf2",
        salt_length=8
    )
    return pwhash


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlsdasdasdSsihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)

# Gravatar for comment images
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


# Create the database with Users
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# TODO: Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


# Query the database to get the user ID.
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# Admin only decorator
def admin_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print('Calling decorated function')
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return wrapper


# TODO: Create a User table for all your registered users.
# Configure Database table for USERS
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)

    # Connect User to BlogPost and Comment
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="author")


# Configure Database table for POSTS
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

    # Connect blog post to author
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="posts")

    # Connect blogpost to comments
    comments = relationship("Comment", back_populates="post")


# Configure database table for COMMENTS
class Comment(db.Model):
    __table__name = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    # Connect comment to a User
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="comments")

    # Connect comment to a Post
    post_id: Mapped[int] = mapped_column(ForeignKey("blog_posts.id"))
    post: Mapped["BlogPost"] = relationship(back_populates="comments")


# Create the databases
with app.app_context():
    db.create_all()


# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods=["GET", "POST"])
def register():
    register_form = RegisterForm()

    if request.method == "GET":
        return render_template("register.html", form=register_form)

    elif request.method == "POST":

        # Check if the email address already exists or not
        if db.session.execute(db.select(User).where(User.email == request.form["email"])).scalar():
            # If yes, redirect the user to login page instead.
            error = "Email already exists. Login instead."
            return redirect(url_for("login", error=error))

        else:

            # If user doesn't exist yet, allow registration
            # Hash / salt the user's password
            user = User(
                email=register_form.email.data,
                password=hash_password(register_form.pwd.data),
                name=register_form.name.data
            )

            # Commit to the database
            db.session.add(user)
            db.session.commit()

            # Log the user in upon registration
            login_user(user)

            # Redirect to the homepage
            return redirect(url_for('get_all_posts'))

# TODO: Retrieve a user from the database based on their email.
@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()

    # Check if the user is registering twice. If yes, flash an error
    error = request.args.get("error")

    if request.method == "GET":
        return render_template("login.html", form=login_form, error=error)

    # If user keys in login form
    if request.method == "POST":
        # Collect the user's keyed in details and check if the user exists in the database
        email = login_form.email.data
        pwd = login_form.pwd.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()

        # If the user exists
        if user:

            # Log user in if password is correct
            if check_password_hash(user.password, pwd):
                login_user(user)
                flash('You were successfully logged in')
                return redirect(url_for('get_all_posts'))

            # If password is incorrect, show an error
            else:
                error = "Password is incorrect"
                return render_template("login.html", form=login_form, error=error)

        # If user doesn't exist, show an error
        else:
            error = "Email doesn't exist"
            return render_template("login.html", form=login_form, error=error)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()

    # Check if anyone comments on the Post
    if request.method == "POST":

        # Check if the person is logged in
        if not current_user.is_authenticated:

            return redirect(url_for("login", error="You need to be logged in to comment"))

        # Add comment to database
        if form.validate_on_submit():
            new_comment = Comment(text=form.text.data,
                                  author=current_user,
                                  post=db.get_or_404(BlogPost, post_id))
            db.session.add(new_comment)
            db.session.commit()

    # Render the post and post comments
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post, form=form)


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):

    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
