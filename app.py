# Імпортуємо необхідні модулі
from flask import Flask, request, render_template, session
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import secrets
import os

# Створіть екземпляр класу Flask
app = Flask(__name__)

# Встановіть секретний ключ для застосунку
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)

# Встановіть CSRF-захист для застосунку
app.config['WTF_CSRF_ENABLED'] = True

# Створіть екземпляр класу CSRFProtect
csrf = CSRFProtect(app)

# Створіть ліміт на кількість запитів до застосунку
limiter = Limiter(
    app,
    default_limits=["20 per minute", "15 per 5 seconds"]
)

# Створіть клас для форми зворотного зв'язку
class ContactForm(FlaskForm):
    name = StringField('Ім\'я', validators=[DataRequired()])
    email = StringField('Електронна пошта', validators=[DataRequired(), Email()])
    message = TextAreaField('Повідомлення', validators=[DataRequired()])
    captcha = StringField('Капча', validators=[DataRequired()])
    submit = SubmitField('Надіслати')

    # Валідатор для капчі
    def validate_captcha(form, field):
        if field.data != session.get('captcha'):
            raise ValidationError('Неправильна капча')

# Маршрут для головної сторінки
@app.route('/')
@limiter.limit("10 per minute")
def index():
    # Генеруємо випадкову капчу
    captcha = secrets.token_urlsafe(4)
    session['captcha'] = captcha
    form = ContactForm()
    return render_template('index.html', form=form, captcha=captcha)

# Маршрут для відправки форми
@app.route('/submit', methods=['POST'])
@limiter.limit("15 per 5 seconds")
def submit_form():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data
        print(f"Received message from {name} ({email}): {message}")
        return f"Дякуємо, {name}! Ваше повідомлення отримано."
    return "Помилка: Невірно введені дані або неправильна капча."

# Запустіть застосунок у режимі відлагодження
if __name__ == '__main__':
    app.run(debug=True)