import os
import secrets
from flask import Flask, render_template, redirect, request, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import or_
from forms.posts import PostForm
from forms.user import RegisterForm, LoginForm, AboutForm
from data.posts import Posts
from data.users import User
from data.messages import Message
from data import db_session
import datetime

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'secret_key'


def main():
    db_session.global_init("db/blogs.db")
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        posts = db_sess.query(Posts).order_by(Posts.id.desc())
        form = PostForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            posts = Posts()
            posts.text = " ".join(i for i in form.text.data.split() if len(i) <= 20)
            file = form.images.data
            if file:
                filename = ".".join([secrets.token_urlsafe(15), file.filename.split(".")[-1]])
                file.save(os.path.join("static/images/post", filename))
                posts.images = filename
            posts.created_date = f'{datetime.datetime.now():%Y-%m-%d %H:%M}'
            current_user.posts.append(posts)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
        return render_template("feed.html", title="PetChat", posts=posts, form=form)
    return render_template("index.html", title="PetChat")


@app.route('/post_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def post_delete(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).filter(Posts.id == id, Posts.user == current_user).first()
    if post:
        db_sess.delete(post)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route("/about")
def about():
    return render_template("index.html", title="PetChat")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form, message="Такой пользователь уже есть")
        user = User(name=form.name.data, email=form.email.data.lower())
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
        user = db_sess.query(User).filter(User.email == form.email.data.lower()).first()
        db_sess.close()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', title='Авторизация', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/settings", methods=['GET', 'POST'])
def settings():
    if current_user.is_authenticated:
        form = AboutForm()
        if form.validate_on_submit():
            file = form.photo.data
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == current_user.id).first()
            if user:
                user.name = form.name.data
                user.email = form.email.data
                user.about = form.about.data
                if file:
                    filename = ".".join([secrets.token_urlsafe(15), file.filename.split(".")[-1]])
                    file.save(os.path.join("static/images/avatars", filename))
                    user.avatar = filename
                db_sess.commit()
                return redirect('/settings')
            else:
                abort(404)
        return render_template("settings.html", title="Настройки", form=form)
    return redirect('/')


@app.route("/profile/<int:user_id>")
def profile(user_id):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        posts = db_sess.query(Posts).filter(Posts.user_id == user_id)
        profile = db_sess.query(User).get(user_id)
        return render_template("profile.html", title="Профиль", posts=posts.all(), profile=profile)
    return redirect('/')


@app.route("/message/<int:user_id>")
def message(user_id):
    if current_user.is_authenticated and current_user.id != user_id:
        db_sess = db_session.create_session()
        messages = db_sess.query(Message).filter(or_((Message.sender == user_id) & (Message.receiver == current_user.id), (Message.receiver == user_id) & (Message.sender == current_user.id))).all()
        receiver = db_sess.query(User).get(user_id)
        dialogs = db_sess.query(Message).filter(Message.receiver == current_user.id).group_by(Message.sender).order_by(Message.id.desc()).all()
        return render_template("messages.html", title="Мессенджер", messages=messages, receiver=receiver, dialogs=dialogs)
    return redirect('/')


@app.route("/message")
def dialogs():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        dialogs = db_sess.query(Message).filter(Message.receiver == current_user.id).group_by(Message.sender).order_by(Message.id.desc()).all()
        return render_template("dialogs.html", title="Мессенджер", dialogs=dialogs)
    return redirect('/')


@app.route('/message_send', methods=['POST'])
@login_required
def message_send():
    if request.form["text"]:
        db_sess = db_session.create_session()
        message = Message()
        message.text = request.form["text"]
        message.sender = request.form["sender_id"]
        message.receiver = request.form["recipient_id"]
        message.time = f'{datetime.datetime.now():%Y-%m-%d %H:%M:%S}'
        # file = request.form["file"]
        # if file:
        #     filename = ".".join([secrets.token_urlsafe(15), file.filename.split(".")[-1]])
        #     file.save(os.path.join("static/images/post", filename))
        #     message.images = filename
        current_user.message.append(message)
        db_sess.merge(current_user)
        db_sess.commit()
        return jsonify({"text": request.form["text"]})
    return jsonify([])


@app.route('/message_get/<int:user_id>', methods=['GET'])
@login_required
def message_get(user_id):
    db_sess = db_session.create_session()
    last_message = db_sess.query(Message).filter(Message.receiver == user_id).order_by(Message.id.desc()).first()
    db_sess.close()
    time = datetime.datetime.now()
    if last_message:
        if datetime.datetime.strptime(last_message.time, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=5) > time:
            return jsonify({'text': last_message.text, "sender_id": last_message.sender, "recipient_id": user_id})
    return jsonify({'text': ""})


@app.route('/users_search/<name>', methods=['GET'])
@login_required
def users_search(name):
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter(User.name.like(f"%{name}%")).order_by(User.name).all()
    db_sess.close()
    if users:
        return jsonify([{'id': user.id, 'avatar': user.avatar, 'name': user.name} for user in users])
    return jsonify([])


if __name__ == '__main__':
    main()