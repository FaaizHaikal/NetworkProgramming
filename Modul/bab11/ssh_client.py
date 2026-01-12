import paramiko
from mock import MagicMock, patch
import unittest

class SSHClient:
  def __init__(self, host, username, password):
    self.host = host
    self.username = username
    self.password = password
    self.client = None
    
  def connect(self):
    self.client = paramiko.SSHClient()
    # self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self.client.connect(self.host, self.username, self.password)
    
  def send_cmd(self, cmd):
    stdin, stdout, stderr = self.client.exec_command(cmd)
    
    output = stdout.read().decode()
    error = stderr.read().decode()
    
    print(f"Output:\n{output}")
    if error:
      print(f"Errors:\n{error}")
      
  def close(self):
    self.client.close()
    
# from paramiko.server import ServerInterface
# from paramiko import RSAKey, Transport
# import socket
# import threading

# class MySSHServer(ServerInterface):
#     def check_auth_password(self, username, password):
#         # Accept all username/password combinations
#         print(f"Login attempt: {username}/{password}")
#         return paramiko.AUTH_SUCCESSFUL
    
#     def check_channel_request(self, kind, chanid):
#         return paramiko.OPEN_SUCCEEDED

# def start_dummy_server(port=2200):
#     host_key = RSAKey.generate(2048)
    
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     sock.bind(('localhost', port))
#     sock.listen(100)
    
#     print(f"Listening on port {port}...")
    
#     while True:
#         client, addr = sock.accept()
#         print(f"Connection from {addr}")
        
#         transport = Transport(client)
#         transport.add_server_key(host_key)
#         transport.start_server(server=MySSHServer())
        
#         # Start a new thread for each connection
#         threading.Thread(target=transport.accept).start()

# if __name__ == '__main__':
#     start_dummy_server()