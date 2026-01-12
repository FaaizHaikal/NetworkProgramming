import socket
import unittest
from unittest import mock
from unittest.mock import patch, MagicMock
import sys
from io import StringIO
import xmlrpc.client

# The function to be tested
def perform_xmlrpc_calls():
    # Connect to the server
    with xmlrpc.client.ServerProxy("http://localhost:8000/") as proxy:
        print("Factorial of 5 is %d" % int(proxy.factorial(5)))
        print("Is 29 a prime number? %s" % str(proxy.is_prime(29)))
        print("Is 30 a prime number? %s" % str(proxy.is_prime(30)))
    

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')

# Unit test class
class TestPerformXmlrpcCalls(unittest.TestCase):
    @patch('xmlrpc.client.ServerProxy')
    def test_perform_xmlrpc_calls(self, MockServerProxy):
        # Create a mock instance of ServerProxy
        mock_proxy = MagicMock()
        
        # Configure the mock to return specific values
        mock_proxy.factorial.return_value = 120
        mock_proxy.is_prime.side_effect = [True, False, True, False]  # Add extra values to avoid StopIteration
        
        # Assign the mock instance to the ServerProxy patch
        MockServerProxy.return_value.__enter__.return_value = mock_proxy
        
        perform_xmlrpc_calls()
        
        # Check if the factorial method was called with expected arguments
        mock_proxy.factorial.assert_called_once_with(5)
        assert_equal(mock_proxy.factorial(5), 120)

        # Check if the is_prime method was called with expected arguments
        mock_proxy.is_prime.assert_any_call(29)
        mock_proxy.is_prime.assert_any_call(30)
        
        # Add print statements to show the test results
        assert_equal(mock_proxy.is_prime(29), True)
        assert_equal(mock_proxy.is_prime(30), False)

# Run the unit tests
if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        perform_xmlrpc_calls()
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
