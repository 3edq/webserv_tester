import sys

sys.path.append("../")
import config
from send_request import send_request

# test rfc7230 section 3.2.4: Field Parsing

def test_space_before_colon() -> str:
    request_header = "GET / HTTP/1.1\r\nHost :{}\r\n\r\n".format(config.SERVER_NAME)
    http_response = send_request(request_header)
    if http_response.status != 400:
        return "Bad status code: {}, expected: {}".format(
            str(http_response.status), "400"
        )
    request_header = (
        "GET / HTTP/1.1\r\nHost:{}\r\nAccept-Language :hyeyoo\r\n\r\n".format(
            config.SERVER_NAME
        )
    )
    http_response = send_request(request_header)
    if http_response.status != 400:
        return "Bad status code: {}, expected: {}".format(
            str(http_response.status), "400"
        )
    return ""

def test_missing_header_name() -> str:
    request_header = "GET / HTTP/1.1\r\nHost:{}\r\n:empty_name\r\n\r\n".format(
        config.SERVER_NAME
    )
    http_response = send_request(request_header)
    if http_response.status // 100 != 4:
        return "Bad status code: {}, expected: {}".format(
            str(http_response.status), "4XX"
        )
    return ""

def test_missing_header_data() -> str:
    request_header = "GET / HTTP/1.1\r\nHost:{}\r\nempty_data:\r\n\r\n".format(
        config.SERVER_NAME
    )
    http_response = send_request(request_header)
    if http_response.status // 100 != 4:
        return "Bad status code: {}, expected: {}".format(
            str(http_response.status), "4XX"
        )
    return ""

def test_missing_header_colon() -> str:
    request_header = "GET / HTTP/1.1\r\nHost:{}\r\nempty_data\r\n\r\n".format(
        config.SERVER_NAME
    )
    http_response = send_request(request_header)
    if http_response.status // 100 != 4:
        return "Bad status code: {}, expected: {}".format(
            str(http_response.status), "4XX"
        )
    return ""

def test_header_too_long() -> str:
    long_text = "T" * 10000000
    request_header = (
        "GET / HTTP/1.1\r\nHost: {}\r\nUser-Agent: {}\r\n\r\n".format(config.SERVER_NAME2,long_text)
    )
    http_response = send_request(request_header)
    # print(http_response.status)
    if http_response.status // 100 != 4:
        return "Bad status code: {}, expected: {} (NOT MANDATORY)".format(
            str(http_response.status), "4XX"
        )
    return ""


def test_headers() -> str:
    request_header = "GET / HTTP/1.1\r\nHost:{}\r\n\r\n".format(config.SERVER_NAME)
    http_response = send_request(request_header)
    if http_response.status != 200:
        return "Bad status code: {}, expected: {}".format(
            str(http_response.status), "200"
        )
    headers = http_response.headers
    #print(headers)
    if (
        headers["Content-Length"] == None
        or headers["Date"] == None
    ):
        return "Missing headers"
    return ""