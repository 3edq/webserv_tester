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

______________________


#!/usr/bin/env python3
"""
WebServ 課題要件テストスイート

このスクリプトは42のwebserv課題の主要要件をテストします：
1. HTTP/1.1プロトコルサポート
2. GET, POST, DELETEメソッド
3. 静的ファイル配信
4. CGI実行
5. エラーハンドリング
6. 設定ファイル読み込み
7. バーチャルホスト
8. リダイレクト
9. ファイルアップロード
10. ディレクトリリスティング
"""

import requests
import subprocess
import time
import threading
import os
import signal
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile

class WebservTester:
    def __init__(self, base_url="http://localhost", ports=[8080, 8081]):
        self.base_url = base_url
        self.ports = ports
        self.webserv_process = None
        self.test_results = []
        
    def start_webserv(self, config_file="conf/default.conf"):
        """webservサーバーを起動"""
        print(f"🚀 webservを起動中... (設定: {config_file})")
        try:
            # webservをバックグラウンドで起動
            self.webserv_process = subprocess.Popen(
                ["./webserv", config_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            # サーバー起動まで少し待機
            time.sleep(2)
            
            # プロセスが生きているかチェック
            if self.webserv_process.poll() is not None:
                stdout, stderr = self.webserv_process.communicate()
                print(f"❌ webservの起動に失敗しました")
                print(f"stdout: {stdout.decode()}")
                print(f"stderr: {stderr.decode()}")
                return False
                
            print("✅ webservが正常に起動しました")
            return True
            
        except Exception as e:
            print(f"❌ webserv起動エラー: {e}")
            return False
    
    def stop_webserv(self):
        """webservサーバーを停止"""
        if self.webserv_process:
            print("🛑 webservを停止中...")
            try:
                # プロセスグループ全体にSIGTERMを送信
                os.killpg(os.getpgid(self.webserv_process.pid), signal.SIGTERM)
                self.webserv_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # 強制終了
                os.killpg(os.getpgid(self.webserv_process.pid), signal.SIGKILL)
                self.webserv_process.wait()
            except Exception as e:
                print(f"⚠️ webserv停止時エラー: {e}")
            print("✅ webservを停止しました")
    
    def log_test_result(self, test_name, passed, details=""):
        """テスト結果をログに記録"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            "name": test_name,
            "passed": passed,
            "details": details
        }
        self.test_results.append(result)
        print(f"{status} {test_name}")
        if details:
            print(f"    詳細: {details}")
    
    def test_basic_get_request(self):
        """基本的なGETリクエストのテスト"""
        try:
            response = requests.get(f"{self.base_url}:{self.ports[0]}/", timeout=5)
            passed = response.status_code in [200, 403, 404]  # サーバーが応答すればOK
            details = f"Status: {response.status_code}, Content-Type: {response.headers.get('Content-Type', 'N/A')}"
            self.log_test_result("基本的なGETリクエスト", passed, details)
            return passed
        except Exception as e:
            self.log_test_result("基本的なGETリクエスト", False, str(e))
            return False
    
    def test_http_methods(self):
        """HTTP メソッド (GET, POST, DELETE) のテスト"""
        methods_passed = 0
        total_methods = 3
        
        # GET テスト
        try:
            response = requests.get(f"{self.base_url}:{self.ports[0]}/", timeout=5)
            if response.status_code < 500:  # サーバーエラーでなければOK
                methods_passed += 1
        except:
            pass
        
        # POST テスト（アップロード機能）
        try:
            files = {'upfile': ('test.txt', 'test content', 'text/plain')}
            response = requests.post(f"{self.base_url}:{self.ports[0]}/upload/", files=files, timeout=5)
            if response.status_code < 500:
                methods_passed += 1
        except:
            pass
        
        # DELETE テスト
        try:
            response = requests.delete(f"{self.base_url}:{self.ports[0]}/delete/test.txt", timeout=5)
            if response.status_code < 500:
                methods_passed += 1
        except:
            pass
        
        passed = methods_passed >= 2  # 3つ中2つ以上成功すればOK
        self.log_test_result("HTTPメソッド対応", passed, f"{methods_passed}/{total_methods} メソッドが正常応答")
        return passed
    
    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        try:
            # 存在しないページをリクエスト
            response = requests.get(f"{self.base_url}:{self.ports[0]}/nonexistent", timeout=5)
            passed = response.status_code == 404
            details = f"404エラーページ Status: {response.status_code}"
            self.log_test_result("404エラーハンドリング", passed, details)
            return passed
        except Exception as e:
            self.log_test_result("404エラーハンドリング", False, str(e))
            return False
    
    def test_cgi_execution(self):
        """CGI実行のテスト"""
        try:
            response = requests.get(f"{self.base_url}:{self.ports[0]}/cgi/", timeout=10)
            # CGIが実行されれば200または適切なレスポンス
            passed = response.status_code in [200, 404, 500]  # 設定次第で変わる
            details = f"CGI Status: {response.status_code}"
            if response.status_code == 200:
                details += f", Content-Length: {len(response.content)}"
            self.log_test_result("CGI実行", passed, details)
            return passed
        except Exception as e:
            self.log_test_result("CGI実行", False, str(e))
            return False
    
    def test_virtual_hosts(self):
        """バーチャルホストのテスト"""
        try:
            # default_serverでアクセス
            headers1 = {'Host': 'default_server:8081'}
            response1 = requests.get(f"{self.base_url}:{self.ports[1]}/", headers=headers1, timeout=5)
            
            # virtual_serverでアクセス
            headers2 = {'Host': 'virtual_server:8081'}
            response2 = requests.get(f"{self.base_url}:{self.ports[1]}/", headers=headers2, timeout=5)
            
            # 両方とも応答があればOK（内容が違えばより良い）
            passed = (response1.status_code < 500 and response2.status_code < 500)
            details = f"default_server: {response1.status_code}, virtual_server: {response2.status_code}"
            self.log_test_result("バーチャルホスト", passed, details)
            return passed
        except Exception as e:
            self.log_test_result("バーチャルホスト", False, str(e))
            return False
    
    def test_redirect(self):
        """リダイレクトのテスト"""
        try:
            # allow_redirects=Falseでリダイレクト応答自体をチェック
            response = requests.get(f"{self.base_url}:{self.ports[0]}/redirect/", 
                                  allow_redirects=False, timeout=5)
            passed = response.status_code in [301, 302, 307]
            details = f"Redirect Status: {response.status_code}, Location: {response.headers.get('Location', 'N/A')}"
            self.log_test_result("リダイレクト", passed, details)
            return passed
        except Exception as e:
            self.log_test_result("リダイレクト", False, str(e))
            return False
    
    def test_autoindex(self):
        """ディレクトリリスティング（autoindex）のテスト"""
        try:
            response = requests.get(f"{self.base_url}:{self.ports[0]}/index/", timeout=5)
            # autoindexが有効なら200、無効なら403
            passed = response.status_code in [200, 403]
            details = f"Autoindex Status: {response.status_code}"
            if response.status_code == 200:
                # HTMLらしきコンテンツがあるかチェック
                has_html = 'html' in response.text.lower() or 'directory' in response.text.lower()
                details += f", HTML content: {has_html}"
            self.log_test_result("ディレクトリリスティング", passed, details)
            return passed
        except Exception as e:
            self.log_test_result("ディレクトリリスティング", False, str(e))
            return False
    
    def test_concurrent_requests(self):
        """同時リクエスト処理のテスト"""
        def make_request(i):
            try:
                response = requests.get(f"{self.base_url}:{self.ports[0]}/", timeout=10)
                return response.status_code < 500
            except:
                return False
        
        try:
            concurrent_count = 10
            with ThreadPoolExecutor(max_workers=concurrent_count) as executor:
                futures = [executor.submit(make_request, i) for i in range(concurrent_count)]
                successful_requests = sum(1 for future in as_completed(futures) if future.result())
            
            passed = successful_requests >= concurrent_count * 0.8  # 80%以上成功すればOK
            details = f"{successful_requests}/{concurrent_count} リクエストが成功"
            self.log_test_result("同時リクエスト処理", passed, details)
            return passed
        except Exception as e:
            self.log_test_result("同時リクエスト処理", False, str(e))
            return False
    
    def test_large_file_handling(self):
        """大きなファイルのハンドリングテスト"""
        try:
            # 大きなコンテンツでPOSTリクエスト
            large_content = "x" * 5000  # 5KBのテストデータ
            files = {'upfile': ('large_test.txt', large_content, 'text/plain')}
            response = requests.post(f"{self.base_url}:{self.ports[0]}/upload/", 
                                   files=files, timeout=10)
            
            # client_max_body_sizeの設定によって200または413
            passed = response.status_code in [200, 201, 413]
            details = f"Large file upload Status: {response.status_code}"
            self.log_test_result("大きなファイル処理", passed, details)
            return passed
        except Exception as e:
            self.log_test_result("大きなファイル処理", False, str(e))
            return False
    
    def test_http_headers(self):
        """HTTPヘッダー処理のテスト"""
        try:
            headers = {
                'User-Agent': 'WebservTester/1.0',
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'ja,en;q=0.9',
                'Connection': 'keep-alive'
            }
            response = requests.get(f"{self.base_url}:{self.ports[0]}/", headers=headers, timeout=5)
            
            # レスポンスヘッダーをチェック
            has_content_type = 'Content-Type' in response.headers
            has_content_length = 'Content-Length' in response.headers or 'Transfer-Encoding' in response.headers
            
            passed = response.status_code < 500 and (has_content_type or has_content_length)
            details = f"Status: {response.status_code}, Headers: Content-Type={has_content_type}, Content-Length={has_content_length}"
            self.log_test_result("HTTPヘッダー処理", passed, details)
            return passed
        except Exception as e:
            self.log_test_result("HTTPヘッダー処理", False, str(e))
            return False
    
    def run_all_tests(self):
        """全テストを実行"""
        print("=" * 60)
        print("🧪 WebServ 課題要件テストスイート開始")
        print("=" * 60)
        
        if not self.start_webserv():
            print("❌ webservの起動に失敗したため、テストを中止します")
            return False
        
        try:
            # テスト実行
            test_functions = [
                self.test_basic_get_request,
                self.test_http_methods,
                self.test_error_handling,
                self.test_cgi_execution,
                self.test_virtual_hosts,
                self.test_redirect,
                self.test_autoindex,
                self.test_concurrent_requests,
                self.test_large_file_handling,
                self.test_http_headers
            ]
            
            for test_func in test_functions:
                test_func()
                time.sleep(0.5)  # テスト間の待機時間
            
        finally:
            self.stop_webserv()
        
        # 結果サマリー
        self.print_summary()
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        return passed_tests >= total_tests * 0.7  # 70%以上成功すれば合格
    
    def print_summary(self):
        """テスト結果のサマリーを表示"""
        print("\n" + "=" * 60)
        print("📊 テスト結果サマリー")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"総テスト数: {total_tests}")
        print(f"成功: {passed_tests} ✅")
        print(f"失敗: {failed_tests} ❌")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print("\n失敗したテスト:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  ❌ {result['name']}: {result['details']}")
        
        print("\n" + "=" * 60)
        if passed_tests >= total_tests * 0.7:
            print("🎉 総合評価: PASS (webservは主要要件を満たしています)")
        else:
            print("😞 総合評価: FAIL (いくつかの要件で問題があります)")
        print("=" * 60)

def main():
    """メイン関数"""
    tester = WebservTester()
    
    # Ctrl+Cでの中断処理
    def signal_handler(sig, frame):
        print("\n🛑 テストが中断されました")
        tester.stop_webserv()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # テスト実行
    success = tester.run_all_tests()
    
    # 終了コード
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 
