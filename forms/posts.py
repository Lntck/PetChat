from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FileField, DateTimeField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    text = TextAreaField('Текст', validators=[DataRequired()])
    images = FileField("Изображение (png, jpg)", validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    created_date = DateTimeField("Время создания")
    submit = SubmitField("Опубликовать")
