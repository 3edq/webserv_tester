import sys

import socket
import http.client
import io

sys.path.append("../")
from send_request import send_request
import config


def test_error_http_version() -> str:
    request_header = 'GET / HTTP/0.1\r\nHost:{}\r\n\r\n'.format(
        config.SERVER_NAME)
    http_response = send_request(request_header)
    if http_response.status != 505 and http_response.status // 100 != 4:
        return "Bad status code: {}, expected: {}".format(str(http_response.status), '505 or 4XX')
    return ""

def test_request_line_multiple_space() -> str:
    request_header = "GET  /  HTTP/1.1\r\nHost:{}\r\n\r\n".format(config.SERVER_ADDR)
    http_response = send_request(request_header)
    if http_response.status != 400:
        return "Bad status code: {}, expected: {}".format(
            str(http_response.status), "400"
        )
    return ""

def test_request_line_too_long() -> str:
    target = "/" + "A" * (config.MAX_URI_LENGTH - 1)
    request_header = "GET {} HTTP/1.1\r\nHost:{}\r\n\r\n".format(
        target, config.SERVER_ADDR
    )
    try:
        http_response = send_request(request_header)
    except Exception as e:
        return f"Error while sending request: {e}"
    if http_response.status != 414:
        return "Bad status code: {}, expected: {}".format(
            str(http_response.status), "400"
        )
    return ""
