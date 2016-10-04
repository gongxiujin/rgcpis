# -*- coding: utf-8 -*-
from flask_login import current_user
from functools import wraps
import datetime
from rgcpis.config.default import DefaultConfig
from flask import request, flash, redirect
from rgcpis.utils.auth import get_remote_addr, json_response


def update_current_and_lastip(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            current_time = datetime.datetime.now()
            if current_user.update_date and (current_time - current_user.update_date).seconds > 30:
                if current_user.update_date and current_user.update_ip:
                    current_user.lastip = current_user.update_ip
                    current_user.lastseen = current_user.update_date
                current_user.update_date = current_time
                current_user.update_ip = get_remote_addr(request)
                current_user.save()
        return func(*args, **kwargs)

    return decorated_function

def api_check_ipxe_status(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not DefaultConfig.IPXE_STATUS:
            return json_response(1)
        return func(*args, **kwargs)

    return decorated_function

def check_ipxe_status(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not DefaultConfig.IPXE_STATUS:
            flash(u'ipxe不允许被操作', 'danger')
            # flash('sfsds', 'danger')
            return redirect(request.referrer)
        return func(*args, **kwargs)

    return decorated_function

