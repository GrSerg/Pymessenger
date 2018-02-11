from socket import *
import json
import time
import sys
import logging
from log.log_config import *

client_logger = logging.getLogger('client')
log = Log(client_logger)

presense_message = {
    'action': 'presense',
    'time': time.time(),
    'type': 'status',
    'user': {
        'account_name': 'Guest',
        'status': 'Hello'
    }
}


@log
def create_message(message_to, text, account_name='Guest'):
    return {'action': 'msg',
            'time': time.time(),
            'to': message_to,
            'from': account_name,
            'message': text}


@log
def read_messages(client_sock):
    while True:
        print('Чтение')
        message = client_sock.recv(1024)
        message = json.loads(message.decode())
        print('Полное сообщение: {}'.format(message))
        print(message['message'])


@log
def write_message(client_sock):
    while True:
        text = input(':>')
        message = create_message('#all', text)
        message = json.dumps(message).encode()
        client_sock.send(message)


client_sock = socket(AF_INET, SOCK_STREAM)

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
try:
    mode = sys.argv[3]
except IndexError:
    mode = 'r'


client_sock.connect((addr, port))

presense = json.dumps(presense_message).encode()
client_sock.send(presense)

response = client_sock.recv(1024)
response = json.loads(response.decode())
print(response)

if mode == 'r':
    read_messages(client_sock)
elif mode == 'w':
    write_message(client_sock)
else:
    raise Exception('Не верный режим чтения/записи')


