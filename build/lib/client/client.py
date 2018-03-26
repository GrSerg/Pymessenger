import sys
import logging
from socket import socket, AF_INET, SOCK_STREAM
from log.log_config import *
from JIM.protocol import *
from queue import Queue

client_logger = logging.getLogger('client')
log = Log(client_logger)


class Client:
    """Клиент"""

    def __init__(self, login, password, address, port):
        self.login = login
        self.password = get_hash(login, password)
        self.addr = address
        self.port = port
        self.request_queue = Queue()

    def connect(self):
        # Соединяемся с сервером
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.addr, self.port))
        # создаем и отправляем presense сообщение
        presence = self.create_presence()
        send_message(self.sock, presence)
        # Получаем ответ
        response = get_message(self.sock)
        # проверка ответа
        response = response.translate_response(response)
        return response

    def disconnect(self):
        self.sock.close()

    @log
    def create_presence(self):
        """Формирование presence сообщения"""
        jim_presense = JimPresence(self.login, self.password)
        message = jim_presense.to_dict()
        return message

    def create_authenticate(self):
        """Сообщение аутентификации"""
        jim_authenticate = JimAuthenticate(self.login, self.password)
        message = jim_authenticate.to_dict()
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

    # def read_messages(self, sock):
    #     """Чтение сообщений в бесконечном цикле"""
    #     while True:
    #         print('Читаю')
    #         message = get_message(sock)
    #         print(message[MESSAGE])

    def get_contacts(self):
        # запрос на список контактов
        jimmessage = JimGetContacts(self.login)
        send_message(self.sock, jimmessage.to_dict())
        # получаем ответ
        # response = get_message(self.sock)
        # response = Jim.from_dict(response)
        # получаем ответ из очереди
        response = self.request_queue.get()
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
        # message = get_message(self.sock)
        # имена читаем из очереди
        message = self.request_queue.get()
        # возвращаем список имен
        contacts = message.user_id
        return contacts

    def add_contact(self, username):
        # запрос на добавление контакта
        message = JimAddContact(self.login, username)
        send_message(self.sock, message.to_dict())
        # получаем ответ от сервера
        # response = get_message(self.sock)
        # response = Jim.from_dict(response)
        # получаем ответ из очереди
        response = self.request_queue.get()
        return response

    def del_contact(self, username):
        # запрос на удаление контакта
        message = JimDelContact(self.login, username)
        send_message(self.sock, message.to_dict())
        # получаем ответ от сервера
        # response = get_message(self.sock)
        # response = Jim.from_dict(response)
        # получаем ответ из очереди
        response = self.request_queue.get()
        return response

    def send_message(self, to, text):
        # отправка сообщения
        message = JimMessage(to, self.login, text)
        # отправляем
        send_message(self.sock, message.to_dict())

#     def write_messages(self):
#         """Клиент пишет сообщения в бесконечном цикле"""
#         while True:
#             text = input(':>')
#             if text.startswith('list'):
#                 message = self.get_contacts()
#                 for name in message:
#                     print(name)
#             else:
#                 command, param = text.split()
#                 if command == 'add':
#                     response = self.add_contact(param)
#                     if response.response == ACCEPTED:
#                         print('Контакт успешно добавлен')
#                     else:
#                         print(response.error)
#                 elif command == 'del':
#                     response = self.del_contact(param)
#                     if response.response == ACCEPTED:
#                         print('Контакт успешно удален')
#                     else:
#                         print(response.error)
#
#
# if __name__ == '__main__':
#     client = Client('Serg')
#     client.connect()
#     client.write_messages()
