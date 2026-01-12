import socket
import select
import unittest
from unittest import mock
from unittest.mock import patch, MagicMock
import sys
from io import StringIO
import zlib
import os

class FTPServer:
    def __init__(self, host='127.0.0.1', port=2000):
        """Create a new FTP server listening on the specified host and port."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_addr = (host, port)
        server_socket.bind(server_addr)
        print('Listening on 127.0.0.1:2000')
        server_socket.listen(5)
        server_socket.setblocking(False)
        
        self.sock = server_socket
        self.inputs = [self.sock]
        self.client_data = {}

    def start(self):
        while True:
            readable, _, _ = select.select(self.inputs, [], [])
            for s in readable:
                if s is self.sock:
                    client_socket, client_address = self.sock.accept()
                    client_socket.setblocking(False)
                    self.inputs.append(client_socket)
                    self.client_data[client_socket] = b''
                else:
                    try:
                        data = s.recv(1024)
                        if data:
                            self.client_data[s] += data
                            if data.endswith(b'\r\n'):
                                self.handle_client(s)
                        else:
                            s.close()
                            self.inputs.remove(s)
                            del self.client_data[s]
                    except Exception as e:
                        s.close()
                        self.inputs.remove(s)
                        if s in self.client_data:
                            del self.client_data[s]

    def handle_client(self, client_sock):
        """Handle a new client connection."""
        try:
            compressed_data = self.client_data[client_sock]
            data = zlib.decompress(compressed_data).decode('utf-8').strip()
            self.client_data[client_sock] = b''  # Clear the buffer
            
            command = data.split(' ')[0].upper() if ' ' in data else data.upper()
            
            print('Received command:', data)
            
            if command == 'USER':
                response = b'331 Username OK, need password\r\n'
            elif command == 'PASS':
                response = b'230 User logged in\r\n'
            elif command == 'PWD':
                current_dir = os.getcwd()
                response = f'257 "{current_dir}"\r\n'.encode('utf-8')
            elif command == 'QUIT':
                response = b'221 Goodbye\r\n'
                client_sock.sendall(zlib.compress(response))
                client_sock.close()
                self.inputs.remove(client_sock)
                if client_sock in self.client_data:
                    del self.client_data[client_sock]
                return
            else:
                response = b'502 Command not implemented\r\n'
                
            client_sock.sendall(zlib.compress(response))
        except Exception as e:
            error_response = b'500 Error processing command\r\n'
            client_sock.sendall(zlib.compress(error_response))

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

class TestFTPServer(unittest.TestCase):
    def setUp(self):
        self.server = FTPServer()

    def tearDown(self):
        self.server.sock.close()

    def test_handle_client_user(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: zlib.compress(b'USER valid_username\r\n')}
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(zlib.compress(b'331 Username OK, need password\r\n'))

    def test_handle_client_pass(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: zlib.compress(b'PASS valid_password\r\n')}
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(zlib.compress(b'230 User logged in\r\n'))

    def test_handle_client_pwd(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: zlib.compress(b'PWD\r\n')}
        with mock.patch('os.getcwd', return_value='/mock/directory'):
            self.server.handle_client(client_sock)
            client_sock.sendall.assert_called_with(zlib.compress(b'257 "/mock/directory"\r\n'))

    def test_handle_client_quit(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: zlib.compress(b'QUIT\r\n')}
        self.server.inputs.append(client_sock)
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(zlib.compress(b'221 Goodbye\r\n'))
        self.assertEqual(self.server.inputs, [self.server.sock])
        self.assertNotIn(client_sock, self.server.client_data)
        client_sock.close.assert_called_once()

    def test_handle_client_unknown_command(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: zlib.compress(b'UNKNOWN_COMMAND\r\n')}
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(zlib.compress(b'502 Command not implemented\r\n'))

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        ftp_server = FTPServer()
        ftp_server.start()
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)