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
    DHCP_NETWORK_START = '#!ipxe\nset keep-san 1\nchain http://172.20.0.51/winpe/winpe/wimboot.ipxe'
    BOOT_START = '#!ipxe\nsanboot --no-describe --drive 0x80'
    RENEW_SERVICE = ''
    UPLOAD_SERVICE = ''
    SEND_LOGS = False

    LOGIN_VIEW = "auth.login"
    REAUTH_VIEW = "auth.reauth"
    LOGIN_MESSAGE_CATEGORY = "error"
    SECRET_KEY = '470cd86a9656c3e12afca890df438a22'
    SECRET_SALT = 'U dont know what is this'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    WTF_CSRF_CHECK_DEFAULT = False
    # url_blue_point
    AUTH_URL = '/gong'
    USER_URL = '/user'
    SERVICE_URL = '/service'

    SERVICE_MACHINE_IP = {1: ['172.20.1.1', '172.20.1.250'],
                          2: ['172.20.2.1', '172.20.2.250'],
                          3: ['172.20.3.1', '172.20.3.160']}

    SERVICE_STATUS = {1: u'开机', 0: u'关机', 3: u'重装系统中',2: u'重装前引导', 4: u'备份前引导', 5: u'上传版本中', 6: u'安装完毕重启中'}
