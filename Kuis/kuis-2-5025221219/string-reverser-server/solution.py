import json
import pickle
import sys
import socket
from datetime import datetime
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import io
import logging
import select
# Server function for UDP
def handle_client_message(server_socket, data, addr):
    """Handle a single client message."""
    text = data.decode()
    print(f'Received from {addr}: {text}')

    # Reverse the message
    reversed_text = text[::-1]

    # Send the reversed message back to the client
    server_socket.sendto(reversed_text.encode(), addr)

def start_server():
    """Start the UDP server and listen for incoming datagrams."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host = '127.0.0.1'
    port = 12345
    server_address = (host, port)

    # bind the server socket to the specified host and port
    server_socket.bind(server_address)
    print('UDP server listening on 127.0.0.1:12345 ...')

    try:
        while True:
            data, addr = server_socket.recvfrom(1024)
            handle_client_message(server_socket, data, addr)
    except KeyboardInterrupt:
        print("Server shutting down.")
    except ExitLoopException:
        pass  # Used to exit test
    finally:
        # close the server socket
        server_socket.close()

# Exception used to exit test loop early
class ExitLoopException(Exception):
    pass

# 'Null' stream to discard output during test runs
class NullWriter(StringIO):
    def write(self, txt):
        pass

# Unit tests for UDP version
class TestUDPServer(unittest.TestCase):
    @patch('socket.socket')
    def test_handle_client_message(self, mock_socket):
        print('Test handle_client_message ...')
        mock_server_socket = MagicMock()
        mock_addr = ('127.0.0.1', 12345)

        test_message = "Hello, Server! Please reverse this message."
        expected_reversed = ".egassem siht esrever esaelP !revreS ,olleH"
        data = test_message.encode()

        handle_client_message(mock_server_socket, data, mock_addr)

        mock_server_socket.sendto.assert_called_with(expected_reversed.encode(), mock_addr)
        print(f"sendto called with: {mock_server_socket.sendto.call_args}")

    @patch('socket.socket')
    def test_start_server(self, mock_socket):
        print('Test start_server ...')
        mock_server_socket = MagicMock()
        mock_socket.return_value = mock_server_socket

        test_message = b"test"
        mock_addr = ('127.0.0.1', 12345)
        mock_server_socket.recvfrom.side_effect = [(test_message, mock_addr), ExitLoopException()]

        try:
            start_server()
        except ExitLoopException:
            pass

        mock_server_socket.bind.assert_called_once_with(('127.0.0.1', 12345))
        print(f"bind called with: {mock_server_socket.bind.call_args}")

        mock_server_socket.recvfrom.assert_called_with(1024)
        print(f"recvfrom called with: {mock_server_socket.recvfrom.call_args}")

        mock_server_socket.sendto.assert_called_with(b"tset", mock_addr)
        print(f"sendto called with: {mock_server_socket.sendto.call_args}")

        mock_server_socket.close.assert_called_once()
        print(f"close called with: {mock_server_socket.close.call_args}")

if __name__ == '__main__':
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)

    # Uncomment to run the UDP server directly
    # start_server()
