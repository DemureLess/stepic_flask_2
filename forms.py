from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField, HiddenField

from wtforms.validators import DataRequired


class Leadform(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    phone = StringField('Номер телефона', validators=[DataRequired()])
    send_form = SubmitField('Отправка формы', validators=[DataRequired()])
    booking_time = RadioField("Свободное время", validators=[DataRequired()], choices=[('1-2', '1-2 часа в неделю'),
                                                                                       ('3-5', '3-5 часов в неделю'),
                                                                                       ('5-7', '5-7 часов в неделю'),
                                                                                       ('7-10', '7-10 часов в неделю')])
    booking_goal = RadioField("Цель учебы", choices=[('travel', 'Для путешествий'),
                                                     ('learn', 'Для школы'),
                                                     ('work', 'Для работы'),
                                                     ('move', 'Для переезда')], validators=[DataRequired()])


class MessageForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    phone = StringField('Номер телефона', validators=[DataRequired()])
    message = StringField('Сообщение', validators=[DataRequired()])
    send_form = SubmitField('Отправка формы')


class BookingForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    phone = StringField('Номер телефона', validators=[DataRequired()])
    booking_day = HiddenField('booking_day', validators=[DataRequired()])
    booking_time = HiddenField('booking_time', validators=[DataRequired()])
    send_form = SubmitField('Отправка формы')
