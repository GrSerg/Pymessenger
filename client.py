from socket import *
import json
import time
import sys
import logging
from log.log_config import *
from JIM.protocol import *

client_logger = logging.getLogger('client')
log = Log(client_logger)


class WrongModeError(Exception):
    """Неверный режим запуска"""

    def __init__(self, mode):
        self.mode = mode

    def __str__(self):
        return 'Неверный режим запуска {}. Режим запуска должен быть r - чтение или w - запись'.format(self.mode)


class Client:
    """Клиент"""

    def __init__(self, addr='localhost', port=7777, mode='r'):
        self.addr = addr
        self.port = port
        self.mode = mode
        self.client = self.connect()

    def connect(self):
        client_sock = socket(AF_INET, SOCK_STREAM)
        client_sock.connect((self.addr, self.port))
        return client_sock

    @log
    def mainloop(self):
        # отправка presense сообщения
        presense_message = JimMessage(action=PRESENCE, time=time.time())
        self.client.send(bytes(presense_message))

        # получаем ответ в байтах
        presense_response_bytes = self.client.recv(1024)
        presense_response = JimMessage.create_from_bytes(presense_response_bytes)
        # проверяем всё ли хорошо
        if presense_response.response == OK:
            # Всё ок
            if self.mode == 'r':
                print('Чтение')
                while True:
                    bmessage = self.client.recv(1024)
                    jmessage = JimMessage.create_from_bytes(bmessage)
                    print(jmessage.message)
            elif self.mode == 'w':
                # ждем ввода сообщения и шлем на сервер
                message_str = input(':>')
                msg = JimMessage(action=MSG, time=time.time(), message=message_str)
                self.client.send(bytes(msg))
            else:
                raise WrongModeError(self.mode)
        elif presense_response.response == SERVER_ERROR:
            print('Внутрення ошибка сервера')
        elif presense_response.response == WRONG_REQUEST:
            print('Неверный запрос на сервер')
        else:
            print('Неверный код ответа от сервера')


if __name__ == '__main__':

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
        if mode not in ('r', 'w'):
            print('Режим должен быть r - чтение, w - запись')
            sys.exit(0)
    except IndexError:
        mode = 'r'

    client = Client(addr, port, mode)
    client.mainloop()