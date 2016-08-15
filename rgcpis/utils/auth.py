# -*- coding: utf-8 -*-

def get_remote_addr(user_request):
    if user_request.headers.getlist("X-Forwarded-For"):
        ip = user_request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = user_request.remote_addr

    return ip