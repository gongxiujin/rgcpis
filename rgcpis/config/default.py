# -*- coding: utf-8 -*-
import os


class DefaultConfig(object):
    _basedir = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(
        os.path.dirname(__file__)))))
    DEBUG = True
    TESTING = False

    SEND_LOG = False

    INFO_LOG = 'access.log'
    ERROR_LOG = 'error.log'

    SQLALCHEMY_DATABASE_URI = "mysql://root:aima@localhost:3306/cpis_db?charset=utf8mb4"

    SQLALCHEMY_ECHO = False

    WTF_CSRF_SECRET_KEY = 'donottellyou'

    SEND_LOGS = False

    LOGIN_VIEW = "auth.login"
    REAUTH_VIEW = "auth.reauth"
    LOGIN_MESSAGE_CATEGORY = "error"
    SECRET_KEY = '470cd86a9656c3e12afca890df438a22'
    SECRET_SALT = 'U dont know what is this'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # url_blue_point
    AUTH_URL = '/gong'
    SERVICE_URL = '/service'

    SERVICE_MACHINE_IP = {1: ['172.20.1.1', '172.20.1.250'],
                          2: ['172.20.2.1', '172.20.2.250'],
                          3: ['172.20.3.1', '172.20.3.160']}

    SERVICE_STATUS = {1: u'开机', 0: u'关机', 3: u'重启中'}
