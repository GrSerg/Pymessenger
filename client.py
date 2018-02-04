import socket
import json
import time
import sys

presense_message = {
    'action': 'presense',
    'time': time.time(),
    'type': 'status',
    'user': {
        'account_name': 'Serg',
        'status': 'Hello'
    }
}

client_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0)

try:
    addr = sys.argv[1]
except IndexError:
    addr = '127.0.0.1'
try:
    port = int(sys.argv[2])
except IndexError:
    port = 7777
except ValueError:
    print('Порт должен быть целым числом')
    sys.exit(0)

client_sock.connect((addr, port))

presense = json.dumps(presense_message).encode()
client_sock.send(presense)

data = client_sock.recv(1024)
data = json.loads(data.decode())
print(data)
