#!/usr/bin/env python3
"""
WebServ テストスクリプト - あなたのwebservコード専用

このスクリプトはあなたのwebservの動作を確認します。
設定ファイル (conf/default.conf) に基づいてテストを実行します。
"""

import requests
import subprocess
import os
import time
import socket
import signal
import sys
from threading import Thread

# --- 設定 ---
HOST = "127.0.0.1"
PORTS = [8080, 8081]  # default.confに基づく
WEBSERV_CMD = "./webserv"
CONFIG_FILE = "conf/default.conf"

# --- ANSIカラーコード ---
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# グローバル変数
webserv_process = None

def signal_handler(sig, frame):
    """Ctrl+Cでの終了処理"""
    print(f"\n{YELLOW}テストを中断しています...{RESET}")
    stop_server()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def print_title(title: str):
    """セクションタイトルの表示"""
    print(f"\n{CYAN}=== {title} ==={RESET}")

def print_result(test_name: str, success: bool, details: str = ""):
    """テスト結果の表示"""
    status = f"{GREEN}✅ PASS{RESET}" if success else f"{RED}❌ FAIL{RESET}"
    print(f"{status} {test_name}")
    if details:
        print(f"    詳細: {details}")

def start_server():
    """webservサーバーを起動"""
    global webserv_process
    
    print(f"{CYAN}webservを起動中... ({CONFIG_FILE}){RESET}")
    
    # webservの実行ファイルが存在するかチェック
    if not os.path.exists(WEBSERV_CMD):
        print(f"{RED}エラー: {WEBSERV_CMD} が見つかりません{RESET}")
        print(f"{YELLOW}先に 'make' でビルドしてください{RESET}")
        return False
    
    try:
        # webservをバックグラウンドで起動
        webserv_process = subprocess.Popen(
            [WEBSERV_CMD, CONFIG_FILE],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # サーバー起動まで待機
        print("サーバー起動を待機中...")
        time.sleep(3)
        
        # プロセスが生きているかチェック
        if webserv_process.poll() is not None:
            stdout, stderr = webserv_process.communicate()
            print(f"{RED}webservの起動に失敗しました{RESET}")
            print(f"stdout: {stdout.decode()}")
            print(f"stderr: {stderr.decode()}")
            return False
        
        # ポートが開いているかチェック
        if check_port(PORTS[0]):
            print(f"{GREEN}webservが正常に起動しました (ポート: {PORTS}){RESET}")
            return True
        else:
            print(f"{RED}ポート {PORTS[0]} でサーバーが応答していません{RESET}")
            return False
            
    except Exception as e:
        print(f"{RED}webserv起動エラー: {e}{RESET}")
        return False

def stop_server():
    """webservサーバーを停止"""
    global webserv_process
    
    if webserv_process:
        print(f"{CYAN}webservを停止中...{RESET}")
        try:
            webserv_process.terminate()
            webserv_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            webserv_process.kill()
            webserv_process.wait()
        except Exception as e:
            print(f"{YELLOW}停止時エラー: {e}{RESET}")
        print(f"{GREEN}webservを停止しました{RESET}")

def check_port(port):
    """ポートが開いているかチェック"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((HOST, port))
        sock.close()
        return result == 0
    except:
        return False

def send_raw_request(request: str, port: int = PORTS[0]):
    """生のHTTPリクエストを送信"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((HOST, port))
        sock.sendall(request.encode('utf-8'))
        
        response = b""
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            except socket.timeout:
                break
        
        sock.close()
        return response.decode('utf-8', errors='ignore')
    except Exception as e:
        return f"ERROR: {e}"

# --- テスト関数群 ---

def test_basic_get():
    """基本的なGETリクエストのテスト"""
    print_title("基本的なGETリクエスト")
    
    request = "GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
    response = send_raw_request(request)
    
    success = "HTTP/" in response and ("200" in response or "404" in response or "403" in response)
    print(response[:200] + "..." if len(response) > 200 else response)
    print_result("基本的なGET", success, f"レスポンス長: {len(response)} bytes")

def test_post_request():
    """POSTリクエストのテスト (アップロード機能)"""
    print_title("POSTリクエスト (アップロード)")
    
    # マルチパートフォームデータでファイルアップロード
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"upfile\"; filename=\"test.txt\"\r\n"
        f"Content-Type: text/plain\r\n\r\n"
        f"Hello, WebServ!\r\n"
        f"--{boundary}--\r\n"
    )
    
    request = (
        f"POST /upload/ HTTP/1.1\r\n"
        f"Host: localhost\r\n"
        f"Content-Type: multipart/form-data; boundary={boundary}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: close\r\n\r\n"
        f"{body}"
    )
    
    response = send_raw_request(request)
    success = "HTTP/" in response and not "ERROR:" in response
    print(response[:300] + "..." if len(response) > 300 else response)
    print_result("POSTアップロード", success)

def test_delete_request():
    """DELETEリクエストのテスト"""
    print_title("DELETEリクエスト")
    
    request = "DELETE /delete/test.txt HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
    response = send_raw_request(request)
    
    success = "HTTP/" in response and not "ERROR:" in response
    print(response[:200] + "..." if len(response) > 200 else response)
    print_result("DELETE", success)

def test_cgi_execution():
    """CGI実行のテスト"""
    print_title("CGI実行")
    
    request = "GET /cgi/ HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
    response = send_raw_request(request)
    
    success = "HTTP/" in response and not "ERROR:" in response
    print(response[:300] + "..." if len(response) > 300 else response)
    print_result("CGI実行", success)

def test_redirect():
    """リダイレクトのテスト"""
    print_title("リダイレクト")
    
    request = "GET /redirect/ HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
    response = send_raw_request(request)
    
    success = "HTTP/" in response and ("301" in response or "302" in response or "307" in response)
    print(response[:300] + "..." if len(response) > 300 else response)
    print_result("リダイレクト", success, "301/302/307ステータス確認")

def test_directory_listing():
    """ディレクトリリスティングのテスト"""
    print_title("ディレクトリリスティング (autoindex)")
    
    request = "GET /index/ HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
    response = send_raw_request(request)
    
    success = "HTTP/" in response and not "ERROR:" in response
    print(response[:300] + "..." if len(response) > 300 else response)
    print_result("ディレクトリリスティング", success)

def test_error_handling():
    """エラーハンドリングのテスト"""
    print_title("404エラーハンドリング")
    
    request = "GET /nonexistent HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
    response = send_raw_request(request)
    
    success = "HTTP/" in response and "404" in response
    print(response[:300] + "..." if len(response) > 300 else response)
    print_result("404エラー", success, "404ステータス確認")

def test_virtual_hosts():
    """バーチャルホストのテスト (ポート8081)"""
    print_title("バーチャルホスト")
    
    if not check_port(PORTS[1]):
        print(f"{YELLOW}ポート {PORTS[1]} が利用できません{RESET}")
        print_result("バーチャルホスト", False, "ポート8081未起動")
        return
    
    # default_server
    request1 = "GET / HTTP/1.1\r\nHost: default_server:8081\r\nConnection: close\r\n\r\n"
    response1 = send_raw_request(request1, PORTS[1])
    
    # virtual_server
    request2 = "GET / HTTP/1.1\r\nHost: virtual_server:8081\r\nConnection: close\r\n\r\n"
    response2 = send_raw_request(request2, PORTS[1])
    
    print("=== default_server:8081 ===")
    print(response1[:200] + "..." if len(response1) > 200 else response1)
    
    print("\n=== virtual_server:8081 ===")
    print(response2[:200] + "..." if len(response2) > 200 else response2)
    
    success = "HTTP/" in response1 and "HTTP/" in response2
    print_result("バーチャルホスト", success, "両方のホストで応答確認")

def test_static_files():
    """静的ファイル配信のテスト"""
    print_title("静的ファイル配信")
    
    request = "GET /static/ HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
    response = send_raw_request(request)
    
    success = "HTTP/" in response and not "ERROR:" in response
    print(response[:300] + "..." if len(response) > 300 else response)
    print_result("静的ファイル", success)

def test_large_body():
    """大きなボディのテスト"""
    print_title("大きなボディ処理")
    
    # 5KBのテストデータ (client_max_body_sizeは10000に設定されている)
    body = "x" * 5000
    request = (
        f"POST /upload/ HTTP/1.1\r\n"
        f"Host: localhost\r\n"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: close\r\n\r\n"
        f"{body}"
    )
    
    response = send_raw_request(request)
    success = "HTTP/" in response and not "ERROR:" in response
    print(response[:200] + "..." if len(response) > 200 else response)
    print_result("大きなボディ", success, f"ボディサイズ: {len(body)} bytes")

def test_unsupported_method():
    """サポートされていないメソッドのテスト"""
    print_title("サポートされていないメソッド")
    
    request = "PATCH / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
    response = send_raw_request(request)
    
    success = "HTTP/" in response and ("405" in response or "501" in response)
    print(response[:200] + "..." if len(response) > 200 else response)
    print_result("未サポートメソッド", success, "405/501ステータス確認")

# --- メイン実行部 ---
def run_all_tests():
    """全テストを実行"""
    print(f"{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}🧪 WebServ テストスイート開始{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")
    
    # サーバー起動
    if not start_server():
        print(f"{RED}サーバーの起動に失敗したため、テストを中止します{RESET}")
        return False
    
    try:
        # 各テストを実行
        test_basic_get()
        time.sleep(0.5)
        
        test_post_request()
        time.sleep(0.5)
        
        test_delete_request()
        time.sleep(0.5)
        
        test_cgi_execution()
        time.sleep(0.5)
        
        test_redirect()
        time.sleep(0.5)
        
        test_directory_listing()
        time.sleep(0.5)
        
        test_error_handling()
        time.sleep(0.5)
        
        test_virtual_hosts()
        time.sleep(0.5)
        
        test_static_files()
        time.sleep(0.5)
        
        test_large_body()
        time.sleep(0.5)
        
        test_unsupported_method()
        
    finally:
        # サーバー停止
        stop_server()
    
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}🎉 WebServ テスト完了{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")
    print(f"{YELLOW}💡 各テストの出力を確認して、webservの動作を評価してください{RESET}")
    
    return True

if __name__ == "__main__":
    run_all_tests()
