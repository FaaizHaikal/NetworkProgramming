import socket

host='127.0.0.1'
port=12345

address=(host, port)

# create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind to address
server_socket.bind(address)

# listen to incoming address
server_socket.listen(1)

try:
  while True:
    client_socket, addr = server_socket.accept()
    
    print(f"Got a connection from {addr}")
    
    message = client_socket.recv(1024)
    print(f"Message: {message.decode()}")
    
    client_socket.close()
except KeyboardInterrupt:
  print("Server shutting down..")
finally:
  server_socket.close()
