# -*- coding: utf-8 -*-
from rgcpis.user.models import User
import datetime


def create_admin_user(username, password):
    user = User()

    user.username = username
    user.password = password
    user.date_joined = datetime.datetime.now()
    user.status = 1
    user.lastip = '127.0.0.1'

    user.save()
    return user
