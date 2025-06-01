import requests
import subprocess
import os
import time
import config
import socket

def setup_module(module):
    # サーバーを起動
    subprocess.Popen(["python3", "path/to/your/server.py"])
    time.sleep(2)  # サーバーが起動するまで待機

def teardown_module(module):
    # サーバーを停止
    subprocess.call(["pkill", "-f", "path/to/your/server.py"])

def send_request(request):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 8080))  # サーバーのアドレスとポートを指定
    sock.sendall(request.encode('utf-8'))
    response = sock.recv(4096)
    print(response.decode('utf-8'))
    sock.close()

def test_get_request():
    request = (
        "GET / HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "\r\n"
    )
    send_request(request)

def test_post_request():
    request = (
        "POST /post HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "Content-Length: 15\r\n"
        "\r\n"
        "key=value&test=1"
    )
    send_request(request)

def test_delete_request():
    request = (
        "DELETE /delete HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "\r\n"
    )
    send_request(request)

def test_unknown_method():
    request = (
        "UNKNOWN / HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "\r\n"
    )
    send_request(request)

def test_upload_and_download():
    # ファイルをアップロード
    files = {'file': ('test.txt', 'This is a test file')}
    response = requests.post(f"http://localhost:{config.SERVER_PORT}/upload", files=files)
    assert response.status_code == 201

    # ファイルをダウンロード
    response = requests.get(f"http://localhost:{config.SERVER_PORT}/upload/test.txt")
    assert response.status_code == 200
    assert response.text == 'This is a test file'

def test_cgi_get():
    request = (
        "GET /cgi-bin/test.cgi HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "\r\n"
    )
    send_request(request)

def test_cgi_post():
    request = (
        "POST /cgi-bin/test.cgi HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "Content-Length: 9\r\n"
        "\r\n"
        "key=value"
    )
    send_request(request)

def test_large_body():
    body = "a" * 1025
    request = (
        "POST /post/test HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "Content-Length: {}\r\n"
        "\r\n"
        "{}".format(len(body), body)
    )
    send_request(request)

def test_chunked_request():
    request = (
        "POST / HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "Transfer-Encoding: chunked\r\n"
        "\r\n"
        "5\r\nHello\r\n"
        "0\r\n\r\n"
    )
    send_request(request)

def test_redirect():
    request = (
        "GET /redirect HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "\r\n"
    )
    send_request(request)

def test_directory_listing():
    request = (
        "GET /directory/ HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "\r\n"
    )
    send_request(request)

def test_error_handling():
    request = (
        "GET /nonexistent HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "\r\n"
    )
    send_request(request)

def test_multiple_ports():
    request1 = (
        "GET / HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "\r\n"
    )
    request2 = (
        "GET / HTTP/1.1\r\n"
        "Host: localhost:8090\r\n"
        "\r\n"
    )
    send_request(request1)
    send_request(request2)

def test_stress():
    # Siegeを使用してストレステストを実行
    result = subprocess.run(["siege", "-b", f"http://localhost:{config.SERVER_PORT}/"], capture_output=True, text=True)
    assert "Availability: 100.00 %" in result.stdout 

if __name__ == "__main__":
    print("Testing GET request:")
    test_get_request()
    print("\nTesting POST request:")
    test_post_request()
    print("\nTesting DELETE request:")
    test_delete_request()
    print("\nTesting UNKNOWN method:")
    test_unknown_method()
    print("\nTesting large body:")
    test_large_body()
    print("\nTesting chunked request:")
    test_chunked_request()
    print("\nTesting CGI GET:")
    test_cgi_get()
    print("\nTesting CGI POST:")
    test_cgi_post()
    print("\nTesting redirect:")
    test_redirect()
    print("\nTesting directory listing:")
    test_directory_listing()
    print("\nTesting error handling:")
    test_error_handling()
    print("\nTesting multiple ports:")
    test_multiple_ports()
    print("\nTesting upload and download:")
    test_upload_and_download()
    print("\nTesting stress:")
    test_stress() 