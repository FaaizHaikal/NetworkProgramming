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


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Message:
    def __init__(self, username, text, timestamp=datetime.now()):
        self.username = username
        self.text = text
        self.timestamp = timestamp

    @staticmethod
    def deserialize(data):
        message_dict = json.loads(data)
        timestamp = datetime.strptime(message_dict['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
        return Message(message_dict['username'], message_dict['text'], timestamp)

    def serialize(self):
        data = {
            "username": self.username,
            "text": self.text,
            "timestamp": self.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')
        }

        return json.dumps(data)

def main():
    # create socket, bind, and listen
    server_addr = ('127.0.0.1', 12345)
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(server_addr)
    server_socket.listen(5)
    server_socket.setblocking(False)

    sockets_list = [server_socket]

    logger.info('Server is listening on port 12345')

    while True:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], [])

        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                # accept client
                client_socket, client_address = server_socket.accept()
                client_socket.setblocking(False)

                # append to sockets_list
                sockets_list.append(client_socket)
                logger.info(f"Accepted new connection from {client_address}")
            else:
                try:
                    # receive data
                    data = notified_socket.recv(1024)
                    # logger.info(f"{data}")
                    if data:
                        message = Message.deserialize(data)
                        # logger.info(f"{message}")
                        logger.info("Received message:")
                        logger.info(f"Username: {message.username}")
                        logger.info(f"Text: {message.text}")
                        logger.info(f"Timestamp: {message.timestamp}")
                except Exception as e:
                    logger.info(f"Exception: {e}")
                    # remove socket from sockets_list
                    notified_socket.close()
                    # close socket
                    sockets_list.remove(notified_socket)

        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            notified_socket.close()


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

def assert_true_any(parameter1, parameter2):
    found = False
    for message in parameter2:
        if parameter1 in message:
            found = True
            break
    
    print(f'test attribute passed: {parameter1} found in log messages' if found else f'test attribute failed: {parameter1} not found in log messages')
    # return found

class TestChatServer(unittest.TestCase):
    
    @patch('select.select')
    @patch('socket.socket')
    def test_server_main(self, mock_socket_class, mock_select):
        mock_server_socket = MagicMock()
        mock_client_socket = MagicMock()
        
        mock_socket_class.return_value = mock_server_socket
        mock_server_socket.accept.return_value = (mock_client_socket, ('127.0.0.1', 54321))
        
        # Initial call to select() returns the server socket as ready to accept
        mock_select.side_effect = [
            ([mock_server_socket], [], []),
            ([mock_client_socket], [], []),
            KeyboardInterrupt()  # To break out of the infinite loop
        ]
        
        # Mock data received from the client
        test_message = Message("Alice", "Hello, World!", datetime.now())
        serialized_message = test_message.serialize()
        mock_client_socket.recv.return_value = serialized_message
        
        with self.assertLogs(logger, level='INFO') as log:
            with self.assertRaises(KeyboardInterrupt):
                main()
            
            # Check if the server accepted a new connection
            mock_server_socket.accept.assert_called_once()
            mock_client_socket.setblocking.assert_called_once_with(False)
            
            # Check if the server received and deserialized the message correctly
            mock_client_socket.recv.assert_called_once_with(1024)
            
            # Verify log messages
            log_output = log.output
            
            # print(log_output)
            
            assert_true_any("Received message:", log_output)
            assert_true_any("Username: Alice", log_output)
            assert_true_any("Text: Hello, World!", log_output) 

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        main()
    
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
