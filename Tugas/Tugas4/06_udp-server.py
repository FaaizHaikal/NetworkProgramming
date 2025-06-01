import socket
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

def handle_client_message(server_socket):
  message, addr = server_socket.recvfrom(1024)
  message = message.decode()
  print(f"Received from {addr}: {message}")

  if message == "Hello, Server!":
    server_socket.sendto(b'Hello, Client!', addr)
 
def start_server():
  server_address = ('127.0.0.1', 12345)
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  server_socket.bind(server_address)
  
  print(f"UDP server listening on {server_address[0]}:{server_address[1]} ...")
  
  try:
    while True:
      handle_client_message(server_socket)
  except KeyboardInterrupt:
    print("\nServer shutting down...")
  finally:
    server_socket.close()
      
    
class TestServer(unittest.TestCase):
  @patch('socket.socket')
  def test_handle_client_message(self, mock_socket):
    print('Test handle_client_message ...')
    mock_socket_instance = MagicMock()
    mock_socket.return_value = mock_socket_instance

    mock_addr = ('127.0.0.1', 54321)
    mock_socket_instance.recvfrom.return_value = (b'Hello, Server!', mock_addr)

    handle_client_message(mock_socket_instance)

    # Verify calls
    mock_socket_instance.sendto.assert_called_once_with(b'Hello, Client!', ('127.0.0.1', 54321))
    print(f"sendto called with: {mock_socket_instance.sendto.call_args}")
    
  @patch('socket.socket')
  def test_start_server(self, mock_socket):
    print('Test start_server ...')
    mock_sock_instance = MagicMock()
    mock_socket.return_value = mock_sock_instance
        
    # Mock recvfrom to simulate one message then raise KeyboardInterrupt
    mock_sock_instance.recvfrom.side_effect = [
      (b'Hello, Server!', ('127.0.0.1', 54321)),
      ExitLoopException
    ]
        
    # Run the server
    try:
      start_server()
    except ExitLoopException:
      pass
        
    # Verify calls
    mock_sock_instance.bind.assert_called_once_with(('127.0.0.1', 12345))
    print(f"bind called with: {mock_sock_instance.bind.call_args}")

    mock_sock_instance.recvfrom.assert_called_with(1024)
    print(f"recvfrom called with: {mock_sock_instance.recvfrom.call_args}")
    
    mock_sock_instance.close.assert_called_once()

class ExitLoopException(Exception):
  pass

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
  def write(self, txt):
    pass

# Automatically execute the unit tests when the script is run
if __name__ == '__main__':
  # Run unittest with a custom runner that suppresses output
  # Make sure to uncomment this before uploading the code to domjudge
  runner = unittest.TextTestRunner(stream=NullWriter())
  unittest.main(testRunner=runner, exit=False)

  # Uncomment this if you want to run the client program, not running the unit test
  # start_server()
