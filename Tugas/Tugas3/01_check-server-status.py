import unittest
from unittest.mock import patch, MagicMock
import sys
import socket
from io import StringIO

def check_server_status():
    try:
        # Use a context manager to handle the socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to the server
            sock.connect(('jsonplaceholder.typicode.com', 80))

            # Send an HTTP GET request
            request = b'GET /posts HTTP/1.1\r\nHost: jsonplaceholder.typicode.com\r\nConnection: close\r\n\r\n'
            sock.send(request)

            # Receive the response
            response = sock.recv(4096).decode('utf-8')

            # Extract the status code from the response
            status_code = response.split(' ')[1]

    except Exception as e:
        print(f"Error: {e}")
        status_code = None

    return status_code


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')


class TestCheckServerStatus(unittest.TestCase):
    @patch('socket.socket')
    def test_server_up(self, mock_socket):
        # Create a mock socket instance
        print(f'Server is up!')
        mock_socket_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance

        # Simulate server response indicating server is up
        http_response = "HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n"
        mock_socket_instance.recv.return_value = http_response.encode('utf-8')

        # Call the function and verify output
        status_code = check_server_status()

        # Verify that the socket methods were called correctly
        mock_socket_instance.connect.assert_called_with(('jsonplaceholder.typicode.com', 80))
        print(f"connect called with: {mock_socket_instance.connect.call_args}")
        
        mock_socket_instance.send.assert_called_once()  # Ensure 'send' was called
        print(f"send called with: {mock_socket_instance.send.call_args}")

        mock_socket_instance.recv.assert_called_once()  # Ensure 'recv' was called
        print(f"recv called with: {mock_socket_instance.recv.call_args}")

        assert_equal(status_code, '200')

    @patch('socket.socket')
    def test_server_down(self, mock_socket):
        # Mock socket instance for server down scenario
        print(f'Server is down!')
        mock_socket_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance

        # Simulate server response indicating server is down
        http_response = "HTTP/1.1 500 Internal Server Error\r\nContent-Length: 0\r\n\r\n"
        mock_socket_instance.recv.return_value = http_response.encode('utf-8')

        # Call the function and verify output
        status_code = check_server_status()

        # Verify that the socket methods were called correctly
        mock_socket_instance.connect.assert_called_with(('jsonplaceholder.typicode.com', 80))
        print(f"connect called with: {mock_socket_instance.connect.call_args}")
        
        mock_socket_instance.send.assert_called_once()  # Ensure 'send' was called
        print(f"send called with: {mock_socket_instance.send.call_args}")

        mock_socket_instance.recv.assert_called_once()  # Ensure 'recv' was called
        print(f"recv called with: {mock_socket_instance.recv.call_args}")

        assert_equal(status_code, '500')


# The function can be used as follows:
if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        status = check_server_status()
        print(status)

    # run unit test to test locally
    # or for domjudge
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)
