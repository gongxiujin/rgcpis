# -*- coding: utf-8 -*-
import datetime

from flask_wtf import Form, RecaptchaField
from wtforms import (StringField, PasswordField, BooleanField, HiddenField,
                     SubmitField)
from wtforms.validators import (DataRequired, InputRequired, Email, EqualTo,
                                regexp, ValidationError)


USERNAME_RE = r'^[\w.+-]+$'
is_username = regexp(USERNAME_RE,
                     message="You can only use letters, numbers or dashes.")


class LoginForm(Form):
    login = StringField("Username or E-Mail Address", validators=[
        DataRequired(message="A Username is required.")]
    )

    password = PasswordField("Password", validators=[
        DataRequired(message="A Password is required.")])

    remember_me = BooleanField("Remember Me", default=False)

    submit = SubmitField("Login")