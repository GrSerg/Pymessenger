import sys
import logging
from socket import *
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

    def __init__(self, login='Guest'):
        self.login = login

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

    def write_messages(self, sock):
        """Клиент пишет сообщения в бесконечном цикле"""
        while True:
            text = input(':>')
            if text.startswith('list'):
                # запрос на список контактов
                jimmessage = JimGetContacts(self.login)
                send_message(sock,jimmessage.to_dict())
                # получаем ответ
                response = get_message(sock)
                response = Jim.from_dict(response)
                # количество контактов
                quantity = response.quantity
                print('У вас ', quantity, 'друзей')
                # имена друзей по отдельности
                print('Вот они:')
                for i in range(quantity):
                    message = get_message(sock)
                    message = Jim.from_dict(message)
                    print(message.user_id)
            else:
                command, param = text.split()
                if command == 'add':
                    # будем добавлять контакт
                    message = JimAddContact(self.login, param)
                    send_message(sock, message.to_dict())
                    # получаем ответ от сервера
                    response = get_message(sock)
                    response = Jim.from_dict(response)
                    if response.response == ACCEPTED:
                        print('Контакт {} успешно добавлен'.format(param))
                    else:
                        print(response.error)
                elif command == 'del':
                    # будем удалять контакт
                    message = JimDelContact(self.login, param)
                    send_message(sock, message.to_dict())
                    # получаем ответ от сервера
                    response = get_message(sock)
                    response = Jim.from_dict(response)
                    if response.response == ACCEPTED:
                        print('Контакт {} успешно удален'.format(param))
                    else:
                        print(response.error)


if __name__ == '__main__':
    sock = socket(AF_INET, SOCK_STREAM)

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

    sock.connect((addr, port))
    # создаем пользователя
    client = Client('Serg')
    # отправляем presense сообщение
    presense = client.create_presense()
    send_message(sock, presense)
    # получаем и проверяем ответ
    response = get_message(sock)
    response = client.translate_response(response)
    if response == OK:
        # в зависимости от режима мы будем или слушать или отправлять сообщения
        if mode == 'r':
            client.read_messages(sock)
        elif mode == 'w':
            client.write_messages(sock)
        else:
            raise WrongModeError