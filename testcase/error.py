import sys

sys.path.append("../")
import config
from send_request import send_request

def test_invalid_http_version() -> str:
    request_header = "GET / HTTP/1.0\r\nHost: {}\r\n\r\n".format(config.SERVER_NAME)
    http_response = send_request(request_header)
    if http_response.status != 505:
        return "Bad status code for HTTP/1.0: {}, expected: 505".format(http_response.status)
    return ""
