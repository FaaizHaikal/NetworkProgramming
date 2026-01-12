import socket
import unittest
from unittest import mock
from unittest.mock import patch, MagicMock
import sys
from io import StringIO
import zlib

class FTPClient:
    def __init__(self, host='127.0.0.1', port=2000):
        self.host = host
        self.port = port
        self.sock = None
        self.username = 'test'
        self.password = 'pass'
        self.timeout = socket._GLOBAL_DEFAULT_TIMEOUT
        
    def connect(self):
        """Connect to the FTP server."""
        self.sock = socket.create_connection((self.host, self.port), self.timeout)
        resp = self.get_resp()
        if '220' not in resp:
            print(f'{resp}\n')

    def send_command(self, command):
        """Send a command to the FTP server and compress it."""
        compressed_cmd = zlib.compress(command.encode('ascii') + b'\r\n')
        self.sock.sendall(compressed_cmd)
        return self.get_resp()

    def login(self, username, password):
        """Login to the FTP server."""
        resp = self.send_cmd(f'USER {username}')
        if '331' in resp:
          resp = self.send_cmd(f'PASS {password}')
        return resp

    def print_working_directory(self):
        """Print the current working directory."""
        return self.send_command('PWD')
    
    def get_resp(self):
        try:
            resp = self.sock.recv(1024)
            decompressed = zlib.decompress(resp)
            return decompressed.decode('ascii').strip()
        except:
            return ''

    def quit(self):
        """Quit the FTP server."""
        return self.send_command('QUIT')

    def close(self):
        """Close the FTP connection."""
        self.sock.close()

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

class TestFTPClient(unittest.TestCase):

    @patch('socket.socket')
    def test_connect(self, mock_socket):
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.recv.return_value = zlib.compress(b'220 Welcome to the FTP server\r\n')

        client = FTPClient()
        client.connect()
        
        mock_sock_instance.connect.assert_called_once_with(('127.0.0.1', 2000))
        print(f"connect called with {mock_sock_instance.connect.call_args}") 
        mock_sock_instance.recv.assert_called_once_with(1024)
        print(f"recv called with {mock_sock_instance.recv.call_args}")

    @patch('socket.socket')
    def test_send_command(self, mock_socket):
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.recv.return_value = zlib.compress(b'331 Username OK, need password\r\n')

        client = FTPClient()
        client.connect()
        client.send_command("USER test")

        mock_sock_instance.sendall.assert_called_once_with(zlib.compress(b'USER test\r\n'))
        print(f"sendall called with {mock_sock_instance.sendall.call_args}")
        mock_sock_instance.recv.assert_called_with(1024)

    @patch('socket.socket')
    def test_print_working_directory(self, mock_socket):
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.recv.return_value = zlib.compress(b'257 "/mock/directory"\r\n')

        client = FTPClient()
        client.connect()
        client.print_working_directory()

        mock_sock_instance.sendall.assert_called_once_with(zlib.compress(b'PWD\r\n'))
        print(f"sendall called with {mock_sock_instance.sendall.call_args}")
        mock_sock_instance.recv.assert_called_with(1024)

    @patch('socket.socket')
    def test_quit(self, mock_socket):
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.recv.return_value = zlib.compress(b'221 Goodbye\r\n')

        client = FTPClient()
        client.connect()
        client.quit()

        mock_sock_instance.sendall.assert_called_once_with(zlib.compress(b'QUIT\r\n'))
        print(f"sendall called with {mock_sock_instance.sendall.call_args}")
        mock_sock_instance.recv.assert_called_with(1024)

    @patch('socket.socket')
    def test_close(self, mock_socket):
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance

        client = FTPClient()
        client.connect()
        client.close()

        mock_sock_instance.close.assert_called_once()

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        ftp_client = FTPClient()
        ftp_client.connect()
        ftp_client.login("user", "pass")
        ftp_client.print_working_directory()
        ftp_client.quit()
        ftp_client.close()
    
    else:
        runner = unittest.TextTestRunner()
        unittest.main(testRunner=runner, exit=False)
