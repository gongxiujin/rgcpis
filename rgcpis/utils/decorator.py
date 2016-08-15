from flask_login import current_user
from functools import wraps
import datetime
from flask import request
from rgcpis.utils.auth import get_remote_addr


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
