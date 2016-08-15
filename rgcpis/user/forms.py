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
    login = StringField(u"用户名", validators=[
        DataRequired(message=u"用户名是必填项")]
    )

    password = PasswordField(u"密码", validators=[
        DataRequired(message=u"密码是必填项.")])

    remember_me = BooleanField("Remember Me", default=False)

    submit = SubmitField("Login")