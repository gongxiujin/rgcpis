# -*- coding: utf-8 -*-
import datetime

from flask_wtf import Form, RecaptchaField
from wtforms import (StringField, PasswordField, BooleanField, HiddenField,
                     SubmitField, Field)
from wtforms.validators import (DataRequired, InputRequired, Email, EqualTo,
                                regexp, ValidationError)

IPADDRESS_RE = r'((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))'
is_ipadd = regexp(IPADDRESS_RE, message='ip address error')


class AddMachineForm(Form):
    startip = StringField(u'添加开始IP', validators=[DataRequired(message=u"必填的"), ])
    endip = StringField(u'添加结束IP', validators=[DataRequired(message=u"必填的"), is_ipadd])
    submit = SubmitField(u'提交')

    def validate_startip(self, field):
        if not is_ipadd:
            raise ValidationError('ip address error')

    def validate_endip(self, field):
        if not is_ipadd:
            raise ValidationError('ip address error')
        end_ips = [int(f) for f in field.data.split('.')]
        start_ips = [int(i) for i in self.startip.data.split('.')]
        if end_ips[0] != start_ips[0] or end_ips[1] != start_ips[1]:
            raise ValidationError('ip address error')
