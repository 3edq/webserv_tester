import requests
import subprocess
import os
import time
import config

def setup_module(module):
    # サーバーを起動
    subprocess.Popen(["python3", "path/to/your/server.py"])
    time.sleep(2)  # サーバーが起動するまで待機

def teardown_module(module):
    # サーバーを停止
    subprocess.call(["pkill", "-f", "path/to/your/server.py"])

def test_get_request():
    response = requests.get(f"http://localhost:{config.SERVER_PORT}/")
    assert response.status_code == 200
    assert "text/html" in response.headers["Content-Type"]

def test_post_request():
    response = requests.post(f"http://localhost:{config.SERVER_PORT}/post", data={"key": "value"})
    assert response.status_code == 201

def test_delete_request():
    response = requests.delete(f"http://localhost:{config.SERVER_PORT}/delete")
    assert response.status_code == 200

def test_unknown_method():
    response = requests.request("UNKNOWN", f"http://localhost:{config.SERVER_PORT}/")
    assert response.status_code == 405

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
    response = requests.get(f"http://localhost:{config.SERVER_PORT}/cgi-bin/test.cgi")
    assert response.status_code == 200

def test_cgi_post():
    response = requests.post(f"http://localhost:{config.SERVER_PORT}/cgi-bin/test.cgi", data={'key': 'value'})
    assert response.status_code == 200

def test_large_body():
    payload = "a" * (config.MAX_BODY_SIZE + 1)
    response = requests.post(f"http://localhost:{config.SERVER_PORT}/post/test", data=payload)
    assert response.status_code == 413

def test_multiple_ports():
    response1 = requests.get(f"http://localhost:{config.SERVER_PORT}/")
    response2 = requests.get(f"http://localhost:{config.SERVER_PORT2}/")
    assert response1.status_code == 200
    assert response2.status_code == 200

def test_error_handling():
    response = requests.get(f"http://localhost:{config.SERVER_PORT}/nonexistent")
    assert response.status_code == 404

def test_directory_listing():
    response = requests.get(f"http://localhost:{config.SERVER_PORT}/directory/")
    assert response.status_code == 200

def test_redirect():
    response = requests.get(f"http://localhost:{config.SERVER_PORT}/redirect", allow_redirects=False)
    assert response.status_code == 301

def test_stress():
    # Siegeを使用してストレステストを実行
    result = subprocess.run(["siege", "-b", f"http://localhost:{config.SERVER_PORT}/"], capture_output=True, text=True)
    assert "Availability: 100.00 %" in result.stdout 