import socket

host='127.0.0.1'
port=12345

address=(host, port)

# create socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to server
client_socket.connect(address)

# send message
message = "Hello, Server!"
client_socket.send(message.encode())
# client_socket.send(b'Hello, Server!')

# close socket
client_socket.close()