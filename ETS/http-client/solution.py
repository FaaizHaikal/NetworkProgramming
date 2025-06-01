import socket
import unittest
from unittest import mock
from unittest.mock import patch, MagicMock
from io import StringIO
import sys


def get_first_length(data):
    header = data.split('\r\n\r\n')[0]
    header_length = len(header)
    for line in header.split('\r\n'):
        if line.lower().startswith('content-length:'):
            parts = line.split(':')
            if len(parts) == 2:
                try:
                    content_length = int(parts[1].strip())
                except ValueError:
                    content_length = 0
        else:
            content_length = 0
    # print(header_length + int(content_length))
    return header_length + int(content_length)

def create_socket():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    client_socket.connect(('localhost', 8080))
    
    return client_socket

def client():
    client_socket = create_socket()
    
    # request = b'HTTP/1.1 200 OK\r\nServer: TestServer\r\n\r\n'
    
    request = b'GET index.html HTTP/1.1\r\nHost: localhost\r\n\r\n'
    
    client_socket.send(request)
    
    response = client_socket.recv(1024).decode()
    
    print(response)
    
    client_socket.close()


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')

class TestHttpClient(unittest.TestCase):
    def test_get_first_length_no_content_length(self):
        print('Testing get_first_length_no_content_length ...')
        data = "HTTP/1.1 200 OK\r\nServer: TestServer\r\n\r\n"
        assert_equal(get_first_length(data), len(data.split('\r\n\r\n')[0]))

    def test_get_first_length_with_content_length(self):
        print('Testing get_first_length_with_content_length ...')
        data = "HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\n12345"
        assert_equal(get_first_length(data), len(data.split('\r\n\r\n')[0]) + 5)

    @patch('socket.socket')
    def test_create_socket(self, mock_socket):
        print('Testing create_socket ...')
        create_socket()
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        instance = mock_socket.return_value
        instance.connect.assert_called_once_with(('localhost', 8080))
        print(f"connect called with: {instance.connect.call_args}")

    @patch('socket.socket')
    def test_client(self, mock_socket):
        print('Testing client ...')
        # Setup the mock socket
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.recv.side_effect = [b'HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\n12345', b'']

        # Call the client function
        client()

        # Check socket methods were called correctly
        mock_sock_instance.connect.assert_called_with(('localhost', 8080))
        print(f"connect called with: {mock_sock_instance.connect.call_args}")

        mock_sock_instance.send.assert_called_once()
        print(f"send called with: {mock_sock_instance.send.call_args}")

        mock_sock_instance.recv.assert_called_once()  # Ensure 'recv' was called
        print(f"recv called with: {mock_sock_instance.recv.call_args}")

        mock_sock_instance.close.assert_called_once()
        print(f"close called with: {mock_sock_instance.close.call_args}")


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        client()

    # run unit test to test locally
    # or for domjudge
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)
    
