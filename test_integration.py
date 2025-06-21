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
YELLOW = "\033[93m"
RESET = "\033[0m"

# テスト結果記録用
test_results = []

# --- サーバ起動・停止 ---
def start_server():
    print(f"{CYAN}Starting webserv server...{RESET}")
    subprocess.Popen(["./webserv", "conf/default.conf"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

def stop_server():
    print(f"{CYAN}Stopping webserv server...{RESET}")
    subprocess.call(["pkill", "-f", "./webserv"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# --- ヘルパー ---
def send_request(request: str, test_name: str):
    print(f"\n{CYAN}=== {test_name} ==={RESET}")
    print(f"Request:\n{request}")
    print(f"{YELLOW}Response:{RESET}")
    
    response = b""
    success = False
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((HOST, PORT))
        sock.sendall(request.encode('utf-8'))
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
        sock.close()
        
        response_str = response.decode('utf-8', errors='ignore')
        print(response_str)
        
        # 基本的な成功判定（HTTPレスポンスが返ってきたか）
        success = response_str.startswith('HTTP/')
        
    except Exception as e:
        print(f"{RED}[ERROR] {e}{RESET}")
        success = False
    
    # テスト結果を記録
    test_results.append((test_name, success))
    print(f"{'-'*60}")

def send_request_port(request: str, test_name: str, port: int):
    print(f"\n{CYAN}=== {test_name} (Port {port}) ==={RESET}")
    print(f"Request:\n{request}")
    print(f"{YELLOW}Response:{RESET}")
    
    response = b""
    success = False
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((HOST, port))
        sock.sendall(request.encode('utf-8'))
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
        sock.close()
        
        response_str = response.decode('utf-8', errors='ignore')
        print(response_str)
        success = response_str.startswith('HTTP/')
        
    except Exception as e:
        print(f"{RED}[ERROR] {e}{RESET}")
        success = False
    
    test_results.append((test_name, success))
    print(f"{'-'*60}")

def test_with_requests(url: str, test_name: str, method: str = "GET", **kwargs):
    print(f"\n{CYAN}=== {test_name} ==={RESET}")
    print(f"URL: {url}")
    print(f"Method: {method}")
    if kwargs:
        print(f"Extra params: {kwargs}")
    print(f"{YELLOW}Response:{RESET}")
    
    success = False
    try:
        if method == "GET":
            res = requests.get(url, **kwargs)
        elif method == "POST":
            res = requests.post(url, **kwargs)
        elif method == "DELETE":
            res = requests.delete(url, **kwargs)
        
        print(f"Status Code: {res.status_code}")
        print(f"Headers: {dict(res.headers)}")
        print(f"Content: {res.text}")
        
        success = res.status_code < 500
        
    except Exception as e:
        print(f"{RED}[ERROR] {e}{RESET}")
        success = False
    
    test_results.append((test_name, success))
    print(f"{'-'*60}")

# --- 各テスト ---
def test_get_request():
    request = "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(request, "GET request")

def test_post_request():
    request = (
        "POST /upload/ HTTP/1.1\r\nHost: localhost\r\n"
        "Content-Length: 15\r\n\r\nkey=value&test=1"
    )
    send_request(request, "POST request")

def test_delete_request():
    request = "DELETE /delete/test.txt HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(request, "DELETE request")

def test_unknown_method():
    request = "UNKNOWN / HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(request, "UNKNOWN method")

def test_large_body():
    body = "a" * 1025
    request = (
        f"POST /upload/ HTTP/1.1\r\nHost: localhost\r\n"
        f"Content-Length: {len(body)}\r\n\r\n{body}"
    )
    send_request(request, "Large body")

def test_chunked_request():
    request = (
        "POST / HTTP/1.1\r\nHost: localhost\r\n"
        "Transfer-Encoding: chunked\r\n\r\n5\r\nHello\r\n0\r\n\r\n"
    )
    send_request(request, "Chunked request")

def test_cgi_get():
    request = "GET /cgi/ HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(request, "CGI GET")

def test_cgi_post():
    request = (
        "POST /cgi/ HTTP/1.1\r\nHost: localhost\r\n"
        "Content-Length: 9\r\n\r\nkey=value"
    )
    send_request(request, "CGI POST")

def test_redirect():
    request = "GET /redirect/ HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(request, "Redirect")

def test_directory_listing():
    request = "GET /index/ HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(request, "Directory listing")

def test_error_handling():
    request = "GET /nonexistent HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(request, "Error handling")

def test_multiple_ports():
    # Port 8080
    request = "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
    send_request(request, "Multiple ports - 8080")
    
    # Port 8081
    request = "GET / HTTP/1.1\r\nHost: default_server:8081\r\n\r\n"
    send_request_port(request, "Multiple ports - 8081", 8081)

def test_upload_and_download():
    # Upload
    files = {'upfile': ('test.txt', 'This is a test file')}
    test_with_requests(f"http://localhost:{PORT}/upload/", "Upload file", "POST", files=files)
    
    # Download
    test_with_requests(f"http://localhost:{PORT}/upload/test.txt", "Download file", "GET")

def print_test_summary():
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}TEST SUMMARY{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")
    
    passed = 0
    total = len(test_results)
    
    for test_name, success in test_results:
        status = f"{GREEN}PASS{RESET}" if success else f"{RED}FAIL{RESET}"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n{CYAN}Results: {passed}/{total} tests passed{RESET}")
    if passed == total:
        print(f"{GREEN}All tests passed!{RESET}")
    else:
        print(f"{YELLOW}{total - passed} tests failed{RESET}")

# --- 実行 ---
if __name__ == "__main__":
    print(f"{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}WebServ Test Suite - Raw Output Mode{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")
    
    start_server()
    
    try:
        test_get_request()
        test_post_request()
        test_delete_request()
        test_unknown_method()
        test_large_body()
        test_chunked_request()
        test_cgi_get()
        test_cgi_post()
        test_redirect()
        test_directory_listing()
        test_error_handling()
        test_multiple_ports()
        test_upload_and_download()
        
    finally:
        stop_server()
        print_test_summary()
