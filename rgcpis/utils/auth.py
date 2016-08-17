# -*- coding: utf-8 -*-
from flask_login import current_app
import json


def get_remote_addr(user_request):
    if user_request.headers.getlist("X-Forwarded-For"):
        ip = user_request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = user_request.remote_addr

    return ip


def ooch_jsonify(*args, **kwargs):
    return current_app.response_class(
        json.dumps(dict(*args, **kwargs)),
        mimetype='application/json'
    )


def json_response(return_code, error_code=None, error_msg=None, **kwargs):
    if error_code:
        return ooch_jsonify(return_code=return_code, error_code=error_code, error_msg=error_msg, **kwargs)
    else:
        return ooch_jsonify(return_code=return_code, **kwargs)

def response_file(data, filename):
    """
    :param data: response data
    :param filename:
    :return: return a file to client
    """
    from flask import Response
    from ctypes import create_string_buffer
    import mimetypes, struct
    from werkzeug.datastructures import Headers
    # buf = create_string_buffer(len(data))
    # struct.pack_into(str(len(data))+"s", buf, 0, data)
    response = Response()
    response.data = data
    response.status_code = 200
    mimetype_tuple = mimetypes.guess_type(filename)
    response.default_mimetype=mimetype_tuple[0]
    response_headers = Headers({
        'Pragma': "no-cache",
        'Expires': '0',
        'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
        'Content-Type': mimetype_tuple[0],
        'Content-Disposition': 'attachment; filename=\"%s\";' % filename,
        'Content-Transfer-Encoding': 'binary',
        'Content-Length': len(response.data)
    })
    if not mimetype_tuple[1] is None:
        response.headers.update({
            'Content-Encoding': mimetype_tuple[1]
        })

    response.headers = response_headers
    return response