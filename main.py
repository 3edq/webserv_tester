import os
import sys

from send_request import send_request
from testcase.content_length import *
from testcase.header_field import *
from testcase.host import *
from testcase.request_line import *
from testcase.error import *
from testcase.get import *
from testcase.post import *
from testcase.put import *
from testcase.chunked import *

from typing import Callable
from tests import *
import config

from colors import *

def cleanup() -> None:

    os.system("rm -rf www/tmp/*")
    os.system("rm -rf www/long.txt")


def run_test(test_name: str, test: Callable) -> None:
    try:
        result = test()
    except:
        print(
            "{}Cannot connect to the server on port {}{}".format(
                C_B_RED, config.SERVER_PORT, RESET
            )
        )
        exit(1)
    char = ""
    color = C_GREEN
    if len(result) == 0:
        char = "✅"
    else:
        color = C_RED
        char = "❌"
    print(r"{:40} {}{} {}{}".format(test_name, color, char, result, RESET))


def run() -> None:
    """
    Entrypoint of the tester
    """
    print(r"{}{}### Normal Tests ###{}".format(C_B_WHITE, B_GRAY, RESET))
    run_test("GET /", test_get)
    run_test("GET page2.html", lambda: test_get_page("page2.html"))
    run_test("GET error.html", lambda: test_get_page("error.html"))
    run_test("GET index1.html", lambda: test_get_page("index1.html"))
    run_test("GET test.html", lambda: test_get_page("test.html"))
    run_test("GET upload.html", lambda: test_get_page("upload.html"))
    run_test("GET random/random.html", lambda: test_get_page("random/random.html"))

    run_test("GET cgi", lambda: test_get_cgi())

    print(r"{}{}### TESTING HEAD ###{}".format(C_B_WHITE, B_GRAY, RESET))
    run_test("HEAD /", test_head)

    print(r"{}{}### TESTING REQUEST LINE ###{}".format(C_B_WHITE, B_GRAY, RESET))
    run_test("GET / HTTP/0.1", test_error_http_version)

    ##Checking if header is \r\n ? could be a check ?
    print(r"{}{}### Headers ###{}".format(C_B_WHITE, B_GRAY, RESET))
    run_test("GET / HTTP/1.1\\r\\nHost :", test_space_before_colon)
    run_test("GET / HTTP/1.1\\r\\nempty:", test_missing_header_name)
    run_test("GET / HTTP/1.1\\r\\n: empty", test_missing_header_data)
    run_test("GET / HTTP/1.1\\r\\nvaluewithnocolon", test_missing_header_colon)

    run_test("Testing mandatory headers", test_headers)

    print(r"{}1. testing host header:{}".format(C_CYAN, RESET))
    run_test("GET / HTTP/1.1\\r\\n\\r\\n", test_missing_host)
    run_test("Host: naver.com\\r\\nHost: hyeyoo.com", test_double_host)
    run_test("Host: xxx\\r\\nHost: xxx", test_multiple_host)


    print(r"{}2. testing content-length header{}".format(C_CYAN, RESET))
    run_test("Content-Length: -1", test_neg_content_length)
    run_test("Content-Length: 10^20", test_big_content_length)
    run_test("Content-Length: NOTDIGIT", test_alpha_content_length)
    # run_test("Content-Length & Chunked", test_length_and_chunked)
    run_test("Content-Length * 2", test_double_length)

    print(r"{}{}### TESTING GET ###{}".format(C_B_WHITE, B_GRAY, RESET))
    run_test("GET /a/", test_get_dir_index)
    run_test("GET /virtual/a/", test_get_dir_not_allowed)
    run_test("GET /b, checking custom 404 page", test_custom_404)
    run_test("GET /doidjo...", test_404)
    run_test("GET /index/a/", test_autoindex)
    run_test("100 GET /", test_multiple_get)
    run_test("GET with different index", test_different_index)
    run_test("GET / on port 8080 and 8081", test_multiple_ports)
    run_test("     /auto, Host: default_server", test_get_dir_no_index)
    run_test("     /auto, Host: google.com", test_get_dir_autoindex)
    run_test("         /, Host: google.com", test_get_dir_index)

    print(r"{}{}### TESTING POST ###{}".format(C_B_WHITE, B_GRAY, RESET))
    run_test("POST /", test_wrong_post)
    run_test("/", test_post_not_allowed)
    run_test("/post/tmp/a.html * 2", test_post)
    run_test("POST /post/test too big payload", test_too_big_request)
    run_test("POST /test.cgi ", test_cgi_headers)

    print(r"{}{}### TESTING CHUNKED ###{}".format(C_B_WHITE, B_GRAY, RESET))
    run_test("Testing read content & trailer", test_chunked_w_trailer)
    run_test("00000", test_chunked_multiplezeros)
    run_test("0", test_DecodeEmptyBodyInPieces)
    run_test("0\\r\\n\\r\\nHello!", test_DecodeEmptyBodyWithExtraStuffAfter)
    run_test("F\\r\\nHello, World!!!", test_DecodeThreeChunksOnePiece)

    print(r"{}{}### TESTING DELETE ###{}".format(C_B_WHITE, B_GRAY, RESET))
    run_test("DELETE /post/gone", test_delete_no_file)



if __name__ == "__main__":
    cleanup()
    run()
