import socket
import re

class FTP:
  def __init__(self, host='localhost', port=21, username='', password='', timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
    self.host = host
    self.port = port
    self.username = username
    self.password = password
    self.timeout = timeout
    self.sock = None
    self.file = None
    self.passive_mode = True
    
  def connect(self):
    self.sock = socket.create_connection((self.host, self.port), self.timeout)
    return self.get_resp()
    
  def login(self):
    resp = self.send_cmd(f'USER {self.username}')
    if '331' in resp:
      resp = self.send_cmd(f'PASS {self.password}')
    return resp
  
  def list(self, path=''):
    data_sock = self._get_data_connection()
    resp = self.send_cmd(f'LIST {path}')
    if not resp.startswith('150'):
      data_sock.close()
      raise Exception(f'LIST failed: {resp}')
    
    data = b''
    while True:
      chunk = data_sock.recv(4096)
      if not chunk:
        break
      data += chunk
    data_sock.close()
    
    _ = self.get_resp()
    return data.decode('ascii')
  
  def download(self, remote_path, local_path):
    data_sock = self._get_data_connection()
    resp = self.send_cmd(f'RETR {remote_path}')
    if not resp.startswith('150'):
      data_sock.close()
      raise Exception(f"RETR failed: {resp}")
    
    with open(local_path, 'wb') as f:
      while True:
        chunk = data_sock.recv(4096)
        if not chunk:
          break
        f.write(chunk)
    data_sock.close()
    
    final_resp = self.get_resp()
    return final_resp
  
  def upload(self, local_path, remote_path):
    data_sock = self._get_data_connection()
    resp = self.send_cmd(f'STOR {remote_path}')
    if not resp.startswith('150'):
      data_sock.close()
      raise Exception(f"STOR failed: {resp}")
      
    with open(local_path, 'rb') as f:
      while True:
        chunk = f.read(4096)
        if not chunk:
          break
        data_sock.sendall(chunk)
    data_sock.close()
    
    final_resp = self.get_resp()
    return final_resp
    
  def get_resp(self):
    resp = ''
    while True:
      line = self.sock.recv(1024).decode('ascii')
      resp += line
      if line.endswith('\r\n'):
        break
    return resp.strip()
    
  def send_cmd(self, cmd):
    self.sock.sendall(cmd.encode('ascii') + b'\r\n')
    return self.get_resp()
  
  def make_dir(self, dir_name='test_dir'):
    return self.send_cmd(f'MKD {dir_name}')
  
  def remove_dir(self, dir_name='test_dir'):
    return self.send_cmd(f'RMD {dir_name}')
  
  def quit(self):
    resp = self.send_cmd('QUIT')
    self.sock.close()
    return resp
    
  def _get_data_connection(self):
    if self.passive_mode:
      resp = self.send_cmd('PASV')
      matches = re.search(r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)', resp)      
      ip = '.'.join(matches.groups()[:4])
      port = int(matches.group(5)) * 256 + int(matches.group(6))
      return socket.create_connection((ip, port), self.timeout)
    raise NotImplementedError('Active mode not implemented')
  
  def rename(self, from_name, to_name):
    resp = self.send_cmd(f'RNFR {from_name}')
    if not resp.startswith('350'):
        return resp
    return self.send_cmd(f'RNTO {to_name}')
  
if __name__ == '__main__':
  ftp = FTP(username='faaiz', password='faaiz1203')
  print(f'CONNECT: {ftp.connect()}')
  print(f'LOGIN: {ftp.login()}')
  print(f'LIST:\n{ftp.list()}')
  
  print(f'MKD: {ftp.make_dir()}')
  print(f'LIST:\n{ftp.list()}')
  print(f'RMD: {ftp.remove_dir()}')
  print(f'LIST:\n{ftp.list()}')
  
  print(f'RNFR: {ftp.rename('test01.txt', 'renamed01.txt')}')
  print(f'LIST:\n{ftp.list()}')
  print(f'RNFR: {ftp.rename('renamed01.txt', 'test01.txt')}')
  print(f'LIST:\n{ftp.list()}')
  
  print(f'RNTO: {ftp.rename('some_dir', 'renamed_dir')}')
  print(f'LIST:\n{ftp.list()}')
  print(f'RNTO: {ftp.rename('renamed_dir', 'some_dir')}')
  print(f'LIST:\n{ftp.list()}')
  
  print(f'QUIT: {ftp.quit()}')
