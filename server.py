import json
import time
import select
import sys
import logging
from socket import *
from log.log_config import *


server_logger = logging.getLogger('server')
log = Log(server_logger)


response_message = {
    'response': 200,
    'time': time.time(),
    'alert': 'OK'
}

@log
def read_requests(r_clients, all_clients):
    """Чтение запросов из списка клиентов"""
    messages = []
    for sock in r_clients:
        try:
            message = sock.recv(1024)
            message = json.loads(message.decode())
            messages.append(message)
        except:
            print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
            all_clients.remove(sock)
    return messages


@log
def write_responses(messages, w_clients, all_clients):
    for sock in w_clients:
        for message in messages:
            try:
                message = json.dumps(message).encode()
                sock.send(message)
            except:
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                sock.close()
                all_clients.remove(sock)


# def server_start():
#     server_sock = socket(AF_INET, SOCK_STREAM)

server = socket(AF_INET, SOCK_STREAM)

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

server.bind((addr, port))
server.listen(15)
print('Сервер запущен!')
server.settimeout(0.2)
clients = []

while True:
    try:
        client, addr = server.accept()  # принятие запроса на соединение от клиента
        client_presense = client.recv(1024)
        client_presense = json.loads(client_presense.decode())
        print(client_presense)
        response = json.dumps(response_message).encode()  # отправка
        client.send(response)
    except OSError as e:
        pass    # таймаут вышел
    else:
        print('Получен запрос на соединение с %s' % str(addr))
        clients.append(client)
    finally:
        # проверка наличия событий ввода-вывода
        wait = 0
        r = []
        w = []
        try:
            r, w, e = select.select(clients, clients, [], wait)
        except:
            pass

        requests = read_requests(r, clients)
        write_responses(requests, w, clients)


