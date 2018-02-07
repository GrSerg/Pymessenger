import socket
import json
import time
import sys
import logging
import log.log_config

server_logger = logging.getLogger('server')

response_message = {
    'response': 200,
    'time': time.time(),
    'alert': 'OK'
}

server_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0)

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

server_sock.bind((addr, port))
server_sock.listen(5)

# server_sock.settimeout(5)

while True:
    client, addr = server_sock.accept()  # принятие запроса на соединение от клиента
    print('Сервер работает!')

    message = client.recv(1024)
    message = json.loads(message.decode())
    print(message)

    response = json.dumps(response_message).encode()  # отправка
    client.send(response)
