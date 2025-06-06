import sys

sys.path.append("../")
from http.client import HTTPResponse
import socket
import config


def send_request(request_header: str) -> str:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((config.SERVER_ADDR, config.SERVER_PORT))
        client.send(request_header.encode())
    except Exception as e:
        print(f"Error {e}")
        http_response = HTTPResponse(client)
        http_response.begin()
        return http_response
    # read and parse http response
    http_response = HTTPResponse(client)
    http_response.begin()
    return http_response
