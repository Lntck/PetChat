import os
import secrets
from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.posts import PostForm
from forms.user import RegisterForm, LoginForm
from data.posts import Posts
from data.users import User
from data import db_session

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/blogs.db")
    app.run()


@app.route("/", methods=['GET', 'POST'])
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        posts = db_sess.query(Posts).order_by(Posts.created_date.desc())
        form = PostForm()
        if form.validate_on_submit():
            file = form.images.data
            if file:
                file = form.images.data
                filename = ".".join([secrets.token_urlsafe(15), file.filename.split(".")[-1]])
                file.save(os.path.join("static/images/post", filename))
            else:
                filename = ""

            db_sess = db_session.create_session()
            posts = Posts()
            posts.text = " ".join(i for i in form.text.data.split() if len(i) <= 20)
            posts.images = filename
            current_user.posts.append(posts)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
        return render_template("feed.html", title="PetChat", posts=posts, form=form)
    else:
        return render_template("index.html", title="PetChat")


@app.route("/about")
def about():
    return render_template("index.html", title="PetChat")


@app.route("/profile/<int:user_id>")
def profile(user_id):
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).filter(Posts.user_id == user_id)
    profile = db_sess.query(User).get(user_id)
    return render_template("profile.html", title="Профиль", posts=posts.all(), profile=profile)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form, message="Такой пользователь уже есть")
        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', title='Авторизация', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


if __name__ == '__main__':
    main()