# -*- coding: utf-8 -*-
import datetime

from flask_wtf import Form, RecaptchaField
from wtforms import (StringField, SelectField, BooleanField, HiddenField,
                     SubmitField, Field)
from wtforms.validators import (DataRequired, InputRequired, Email, EqualTo,
                                regexp, ValidationError)

IPADDRESS_RE = r'((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))'
is_ipadd = regexp(IPADDRESS_RE, message='ip address error')
COPAY_PER_PAGE = 20


class AddMachineForm(Form):
    startip = StringField(u'开始IP', validators=[DataRequired(message=u"必填的"), ])
    endip = StringField(u'结束IP', validators=[DataRequired(message=u"必填的"), is_ipadd])
    option = SelectField(u'操作', default="on", choices=[
        ("on", u'开机'),
        ("soft", u'关机'),
        ("reset", u'重启')])
    submit = SubmitField(u'提交')

    # def validate_startip(self, field):
    #     if not is_ipadd:
    #         raise ValidationError('ip address error')
    #
    # def validate_endip(self, field):
    #     if not is_ipadd:
    #         raise ValidationError('ip address error')
    #     end_ips = [int(f) for f in field.data.split('.')]
    #     start_ips = [int(i) for i in self.startip.data.split('.')]
    #     if end_ips[0] != start_ips[0] or end_ips[1] != start_ips[1]:
    #         raise ValidationError('ip address error')


class SearchServiceForm(Form):
    search_content = StringField(u'搜索')
    search_type = SelectField(u'类型', default="1", choices=[
        ("1", u'ip'),
        ("2", u'版本号'),
        ("3", u'状态')])
    submit = SubmitField(u'搜索')

    def get_result(self, countent=None, search_type=None):
        from rgcpis.service.models import Service, ServiceVersion
        query = self.search_content.data if not countent else countent
        search_type = self.search_type.data if not search_type else search_type
        if query:
            if search_type == '1':
                return Service.query.filter(Service.ip.like('%' + query + '%'))
            elif search_type == '2':
                version_id = ServiceVersion.get_version_id(query)
                return Service.query.filter_by(version_id=version_id) if version_id else None
            else:
                return Service.query.filter(Service.status.like('%' + query + '%'))
        else:
            return Service.query

class PageSetForm(Form):
    page_set = SelectField('page', default='20', choices=[
        ("25", "25"),
        ("50", "50"),
        ("100", "100")])
