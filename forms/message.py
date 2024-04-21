from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FileField, DateTimeField
from wtforms.validators import DataRequired


class MessageForm(FlaskForm):
    text = StringField('Текст', validators=[DataRequired()])
    image = FileField("Изображение (png, jpg)", validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    time = DateTimeField("Время создания")
    submit = SubmitField("Написать")
