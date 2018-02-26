import sys
import logging
from socket import socket, AF_INET, SOCK_STREAM
from log.log_config import *
from JIM.protocol import *

client_logger = logging.getLogger('client')
log = Log(client_logger)


class Client:
    """Клиент"""

    def __init__(self, login, address='localhost', port=7777, mode='w'):
        self.login = login
        self.addr = address
        self.port = port
        self.mode = mode

    def connect(self):
        # Соединяемся с сервером
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.addr, self.port))
        # отправляем presense сообщение
        presence = self.create_presense()
        send_message(self.sock, presence)
        # Получаем ответ
        response = get_message(self.sock)
        response = response.translate_response(response)
        return response

    def disconnect(self):
        self.sock.close()

    @log
    def create_presense(self):
        """Формирование presense сообщения"""
        jim_presense = JimPresense(self.login)
        message = jim_presense.to_dict()
        return message

    @log
    def translate_response(self, response):
        """Разбор ответа сервера"""
        result = Jim.from_dict(response)
        return result.to_dict()

    def create_message(self, message_to, text):
        """Создание сообщения"""
        message = JimMessage(message_to, self.login, text)
        return message.to_dict()

    def read_messages(self, sock):
        """Чтение сообщений в бесконечном цикле"""
        while True:
            print('Читаю')
            message = get_message(sock)
            print(message[MESSAGE])

    def get_contacts(self):
        # запрос на список контактов
        jimmessage = JimGetContacts(self.login)
        send_message(self.sock, jimmessage.to_dict())
        # получаем ответ
        response = get_message(self.sock)
        response = Jim.from_dict(response)
        # количество контактов
        quantity = response.quantity
        # print('У вас ', quantity, 'друзей')
        # # имена друзей по отдельности
        # print('Вот они:')
        # for i in range(quantity):
        #     message = get_message(sock)
        #     message = Jim.from_dict(message)
        #     print(message.user_id)
        # получаем имена одним списком
        message = get_message(self.sock)
        # возвращаем список имен
        return message

    def add_contact(self, username):
        # будем добавлять контакт
        message = JimAddContact(self.login, username)
        send_message(self.sock, message.to_dict())
        # получаем ответ от сервера
        response = get_message(self.sock)
        response = Jim.from_dict(response)
        return response

    def del_contact(self, username):
        # будем удалять контакт
        message = JimDelContact(self.login, username)
        send_message(self.sock, message.to_dict())
        # получаем ответ от сервера
        response = get_message(self.sock)
        response = Jim.from_dict(response)
        return response

    def write_messages(self):
        """Клиент пишет сообщения в бесконечном цикле"""
        while True:
            text = input(':>')
            if text.startswith('list'):
                message = self.get_contacts()
                for name in message:
                    print(name)
            else:
                command, param = text.split()
                if command == 'add':
                    response = self.add_contact(param)
                    if response.response == ACCEPTED:
                        print('Контакт успешно добавлен')
                    else:
                        print(response.error)
                elif command == 'del':
                    response = self.del_contact(param)
                    if response.response == ACCEPTED:
                        print('Контакт успешно удален')
                    else:
                        print(response.error)


if __name__ == '__main__':
    # try:
    #     addr = sys.argv[1]
    # except IndexError:
    #     addr = '127.0.0.1'
    # try:
    #     port = int(sys.argv[2])
    # except IndexError:
    #     port = 7777
    # except ValueError:
    #     print('Порт должен быть целым числом')
    #     sys.exit(0)
    # try:
    #     mode = sys.argv[3]
    #     if mode not in ('r', 'w'):
    #         print('Режим должен быть r - чтение, w - запись')
    #         sys.exit(0)
    # except IndexError:
    #     mode = 'r'
    client = Client('Serg')
    client.connect()
    client.write_messages()
