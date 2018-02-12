import json
import time
import select
import sys
import logging
from socket import *
from log.log_config import *
from JIM.protocol import *


server_logger = logging.getLogger('server')
log = Log(server_logger)



class Server:
    """Базовый класс сервера мессенджера"""
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port

        self.server = self.start()
        # список клиентов
        self.clients = []


    def start(self):
        server = socket(AF_INET, SOCK_STREAM)
        server.bind((self.addr, self.port))
        server.listen(15)
        print('Сервер запущен!')
        server.settimeout(0.2)
        return server

    @log
    def read_requests(self, r_clients):
        """Чтение запросов из списка клиентов"""
        messages = []
        for sock in r_clients:
            try:
                bmessage = sock.recv(1024)
                message = JimMessage.create_from_bytes(bmessage)
                messages.append(message)
            except:
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                self.clients.remove(sock)
        return messages


    @log
    def write_responses(self, messages, w_clients):
        for sock in w_clients:
            for message in messages:
                try:
                    # message = json.dumps(message).encode()
                    sock.send(bytes(message))
                except: # Сокет недоступен, клиент отключился
                    print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                    sock.close()
                    self.clients.remove(sock)


    def get_connection(self):
        try:
            client, addr = self.server.accept()  # принятие запроса на соединение от клиента
            client_presense_bytes = client.recv(1024)
            client_presense_msg = JimMessage.create_from_bytes(client_presense_bytes)
            if client_presense_msg.action == PRESENCE:
                presense_response = JimResponse(RESPONSE=OK, time=time.time())
                client.send(bytes(presense_response))
            else:
                presense_response = JimResponse(RESPONSE=WRONG_REQUEST, time=time.time())
                client.send(bytes(presense_response))
        except OSError as e:
            pass  # таймаут вышел
        else:
            print('Получен запрос на соединение с %s' % str(addr))
            self.clients.append(client)
        finally:
            # проверка наличия событий ввода-вывода
            wait = 0
            r = []
            w = []
            try:
                r, w, e = select.select(self.clients, self.clients, [], wait)
            except:
                pass    # Ничего не делать, если какой-то клиент отключился

            requests = self.read_requests(r)
            self.write_responses(requests, w)

    def mainloop(self):
        while True:
            self.get_connection()

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


serv = Server(addr, port)
serv.mainloop()
