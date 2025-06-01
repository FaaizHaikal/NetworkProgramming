import socket
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

def client_program():
    server_address = ('127.0.0.1', 12345)
    
    # Create UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Send message first
        message = b'Hello, Server!'
        client_socket.sendto(message, server_address)
        
        # Then wait for response
        recv_message, _ = client_socket.recvfrom(1024)
        print(f"Received from server: {recv_message.decode()}")
        
    finally:
        # Ensure socket is closed
        client_socket.close()

class TestClient(unittest.TestCase):
    @patch('socket.socket')
    def test_client_program(self, mock_socket):
        # Setup mock
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        
        # Mock the recvfrom to return expected response
        mock_socket_instance.recvfrom.return_value = (b'Hello, Client!', ('127.0.0.1', 12345))
        
        # Run client
        client_program()
        
        # Verify calls
        mock_socket_instance.sendto.assert_called_once_with(b'Hello, Server!', ('127.0.0.1', 12345))
        print(f"sendto called with: {mock_socket_instance.sendto.call_args}")
        
        mock_socket_instance.recvfrom.assert_called_once_with(1024)
        print(f"recvfrom called with: {mock_socket_instance.recvfrom.call_args}")

        mock_socket_instance.close.assert_called_once()
        print(f"close called with: {mock_socket_instance.close.call_args}")

class NullWriter(StringIO):
    def write(self, txt):
        pass

if __name__ == '__main__':
    # Run unittest with a custom runner that suppresses output
    # Make sure to uncomment this before uploading the code to domjudge
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)

    # Uncomment this if you want to run the client program, not running the unit test
    # client_program()
