import requests
import subprocess
import os
import time
import socket

# --- 設定 ---
HOST = "127.0.0.1"
PORT = 8080

# --- ANSIカラーコード ---
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"

# --- ヘルパー ---
def send_request(request: str, port: int = PORT):
    response = b""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, port))
        sock.sendall(request.encode('utf-8'))
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
        sock.close()
        print(response.decode('utf-8'))
    except Exception as e:
        print(f"{RED}[ERROR]{RESET} {e}")

def print_title(title: str):
    print(f"\n{CYAN}=== {title} ==={RESET}")


# --- 各テスト ---
def test_get_request():
    request = "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(request)

def test_post_request():
    request = (
        "POST /post HTTP/1.1\r\nHost: localhost\r\n"
        "Content-Length: 15\r\n\r\nkey=value&test=1"
    )
    send_request(request)

def test_delete_request():
    request = "DELETE /delete HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(request)

def test_unknown_method():
    request = "UNKNOWN / HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(request)

def test_large_body():
    body = "a" * 1025
    request = (
        f"POST /post/test HTTP/1.1\r\nHost: localhost\r\n"
        f"Content-Length: {len(body)}\r\n\r\n{body}"
    )
    send_request(request)

def test_chunked_request():
    request = (
        "POST / HTTP/1.1\r\nHost: localhost\r\n"
        "Transfer-Encoding: chunked\r\n\r\n5\r\nHello\r\n0\r\n\r\n"
    )
    send_request(request)

def test_cgi_get():
    request = "GET /cgi/cgi.sh HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(request)

def test_cgi_post():
    request = (
        "POST /cgi/say_hello.py HTTP/1.1\r\nHost: localhost\r\n"
        "Content-Length: 9\r\n\r\nkey=value"
    )
    send_request(request)

def test_redirect():
    request = "GET /redirect HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(request)

def test_autoindex():
    request = "GET /index/ HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(request)

def test_error_handling():
    request = "GET /nonexistent HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(request)

def test_multiple_ports():
    request = "GET / HTTP/1.1\r\nHost: default_server\r\n\r\n"
    send_request(request, port=8081)


def test_upload_and_download():
    print_title("Upload file (requests)")
    files = {'file': ('test.txt', 'This is a test file')}
    res = requests.post(f"http://localhost:{PORT}/upload", files=files)
    print(res.status_code, res.text)

    print_title("Download file (requests)")
    res = requests.get(f"http://localhost:{PORT}/upload/test.txt")
    print(res.status_code, res.text)

# --- 実行 ---
if __name__ == "__main__":

    print_title("GET request")
    test_get_request()

    print_title("POST request")
    test_post_request()

    print_title("DELETE request")
    test_delete_request()

    print_title("UNKNOWN method")
    test_unknown_method()

    print_title("Large body")
    test_large_body()

    print_title("Chunked request")
    test_chunked_request()

    print_title("CGI GET")
    test_cgi_get()

    print_title("CGI POST")
    test_cgi_post()

    print_title("Redirect")
    test_redirect()

    print_title("Autoindex")
    test_autoindex()

    print_title("Error handling")
    test_error_handling()

    print_title("Multiple ports")
    test_multiple_ports()

    print_title("Upload and download")
    test_upload_and_download()
