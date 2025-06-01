import requests

# from send_request import send_request
import config
import sys

sys.path.append("../")
sys.path.append("../lib")


def get_base_url() -> str:
    """
    Return the base URL of the server
    """
    return "http://localhost:{}/".format(config.SERVER_PORT)


def test_head() -> str:
    req = requests.head(get_base_url())
    if req.status_code != 501:
        return "Bad status code: {}, expected: {}".format(str(req.status_code), "200")
    if len(req.text) > 0:
        return "Head returned some content."
    return ""

def test_get() -> str:
    req = requests.get(get_base_url())
    if req.status_code != 200:
        return "Bad status code."
    
    with open('documents/index.html', 'r') as file:
        if req.text != file.read():
            return "Bad content."
    
    if req.headers.get("Content-Length") != str(len(req.text)):
        return "Bad Content-Length."
    if req.headers.get("Content-Type") != "text/html; charset=UTF-8":
        return "Bad Content-Type."
    
    return ""

def test_get_page(pageName) -> str:
    path = get_base_url() + pageName
    req = requests.get(path)
    if pageName == "random/random.html":
        pageName = "error/404.html"
        if req.status_code != 404:
            return "Bad status code."
    elif req.status_code != 200:
        return "Bad status code."
    
    try:
        with open(f'documents/{pageName}', 'r', encoding='utf-8') as file:
            if req.text != file.read():
                return "Bad content."
    except FileNotFoundError:
        return "File not found."
    
    if req.headers.get("Content-Length") != str(len(req.text)):
        return "Bad Content-Length."
    if req.headers.get("Content-Type") != "text/html; charset=UTF-8":
        return "Bad Content-Type."
    
    return ""

def test_get_cgi() -> str:
    html_content = """<!DOCTYPE html>
<html>
<body>
<h3>Hello !</h3>
</body>
</html>

"""
    req = requests.get(get_base_url() + "cgi/python.cgi")
    # print(html_content)
    # print(req.text)
    if req.status_code != 200:
        return "Bad status code."
    
    if req.text != html_content:
        return "Bad content."
    return ""

def test_get_dir_index() -> str:
    req = requests.get(get_base_url() + "a")
    if req.status_code != 200:
        return "Bad status code."
    if req.text != "hello":
        return "Bad content."
    return ""


def test_get_dir_not_allowed() -> str:
    req = requests.get(get_base_url() + "virtual/a/")
    # if (req.status_code != 403):
    if req.status_code != 404:
        return "Bad status code."
    return ""


def test_wrong_post() -> str:
    req = requests.post(get_base_url())
    if req.status_code != 405:
        return "Bad status code."
    return ""


def test_too_big_request() -> str:
    payload = "a" * 1025
    req = requests.post(get_base_url() + "post/test", data=payload)
    if req.status_code != 413:
        return "Bad status code: {}, expected: {}".format(req.status_code, 413)
    return ""


def test_custom_404() -> str:
    req = requests.get(get_base_url() + "b")
    if req.status_code != 404:
        return "Bad status code"
    if req.text != "custom404":
        return "Bad error page"
    return ""


def test_404() -> str:
    req = requests.get(
        get_base_url() + "doidjodoeijdosejfoejfseoifjseiofjsejfsejfesjfseofsejiseofj"
    )
    if req.status_code != 404:
        return "Bad status code"
    return ""


def test_autoindex() -> str:
    req = requests.get(get_base_url() + "index/a/")
    if req.status_code != 200:
        return "Bad status code"
    return ""


def test_multiple_ports() -> str:
    req = requests.get(get_base_url())
    if req.text != "hello world":
        return "Bad content on first port."
    req = requests.get("http://localhost:{}/".format(config.SERVER_PORT2))
    if req.text != "second file":
        return "Bad content on second port."
    return ""


def test_different_index() -> str:
    req = requests.get(get_base_url())
    if req.text != "hello world":
        return "Bad first index."
    req = requests.get(get_base_url() + "2/")
    if req.text != "second file":
        return "Bad second index."
    return ""


def test_multiple_get() -> str:
    for i in range(100):
        req = requests.get(get_base_url())
        if req.status_code != 200 or req.text != "hello world":
            return "Bad request at {}th iteration.".format(i + 1)
    return ""


def test_delete_no_file() -> str:
    req = requests.delete(get_base_url() + "post/gone")
    if req.status_code != 404:
        return "Bad status code for DELETE."
    return ""


def test_unknown_method() -> str:
    req = requests.request("UNKNOWN", get_base_url())
    if req.status_code != 405:
        return "Bad status code for unknown method: {}, expected: 405".format(req.status_code)
    return ""

def test_upload_and_download() -> str:
    # Upload a file
    files = {'file': ('test.txt', 'This is a test file')}
    req = requests.post(get_base_url() + "upload", files=files)
    if req.status_code != 201:
        return "Failed to upload file, status code: {}".format(req.status_code)
    
    # Download the file
    req = requests.get(get_base_url() + "upload/test.txt")
    if req.status_code != 200 or req.text != 'This is a test file':
        return "Failed to download file, status code: {}".format(req.status_code)
    return ""

def test_cgi_get() -> str:
    req = requests.get(get_base_url() + "cgi-bin/test.cgi")
    if req.status_code != 200:
        return "Bad status code for CGI GET: {}".format(req.status_code)
    return ""

def test_cgi_post() -> str:
    req = requests.post(get_base_url() + "cgi-bin/test.cgi", data={'key': 'value'})
    if req.status_code != 200:
        return "Bad status code for CGI POST: {}".format(req.status_code)
    return ""

def test_large_body() -> str:
    payload = "a" * (config.MAX_BODY_SIZE + 1)
    req = requests.post(get_base_url() + "post/test", data=payload)
    if req.status_code != 413:
        return "Bad status code for large body: {}, expected: 413".format(req.status_code)
    return ""
