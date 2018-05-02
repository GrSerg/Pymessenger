import select
import sys
import logging
from socket import *
from log.log_config import *
from JIM.protocol import *
from repo.server_models import session
from repo.server_repo import Repo
from repo.server_errors import ContactDoesNotExist

server_logger = logging.getLogger('server')
log = Log(server_logger)


class Handler:
    """Обработчик сообщений"""
    def __init__(self):
        self.repo = Repo(session)

    @log
    def read_requests(self, r_clients, all_clients):
        """Чтение запросов из списка клиентов"""
        # список входящих сообщений
        messages = []
        for sock in r_clients:
            try:
                message = get_message(sock)
                messages.append(message)
            except:
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                all_clients.remove(sock)
        return messages

    @log
    def write_responses(self, messages, w_clients, all_clients):
        """Отправка сообщений клиентам"""
        for sock in w_clients:
            # отправка сообщений всем
            for message in messages:
                try:
                    # теперь нам приходят разные сообщения, будем их обрабатывать
                    action = Jim.from_dict(message)
                    if action.action == GET_CONTACTS:
                        # нам нужен репозиторий
                        contacts = self.repo.get_contacts(action.account_name)
                        response = JimResponse(ACCEPTED, quantity=len(contacts))
                        send_message(sock, response.to_dict())
                        # # в цикле по контактам шлем сообщения
                        # for contact in contacts:
                        #     message = JimContactList(contact.Name)
                        #     print(message.to_dict())
                        #     send_message(sock, message.to_dict())
                        contact_names = [contact.Name for contact in contacts]
                        message = JimContactList(contact_names)
                        send_message(sock, message.to_dict())
                    elif action.action == ADD_CONTACT:
                        user_id = action.user_id
                        username = action.account_name
                        try:
                            self.repo.add_contact(username, user_id)
                            # шлем удачный ответ
                            response = JimResponse(ACCEPTED)
                            send_message(sock, response.to_dict())
                        except ContactDoesNotExist as e:
                            # формируем ошибку, такого контакта нет
                            response = JimResponse(WRONG_REQUEST, error='Такого контакта нет')
                            send_message(sock, response.to_dict())
                    elif action.action == DEL_CONTACT:
                        user_id = action.user_id
                        username = action.account_name
                        try:
                            self.repo.del_contact(username, user_id)
                            # шлем удачный ответ
                            response = JimResponse(ACCEPTED)
                            send_message(sock, response.to_dict())
                        except ContactDoesNotExist as e:
                            # формируем ошибку, такого контакта нет
                            response = JimResponse(WRONG_REQUEST, error='Такого контакта нет')
                            send_message(sock, response.to_dict())
                except WrongInputError as e:
                    # Отправляем ошибку и текст из ошибки
                    response = JimResponse(WRONG_REQUEST, error=str(e))
                    send_message(sock, response.to_dict())
                except:
                    # Сокет недоступен, клиент отключился
                    print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                    sock.close()
                    all_clients.remove(sock)

    def presence_response(self, presence_message):
        """Формирование ответа клиенту"""
        try:
            presence = Jim.from_dict(presence_message)
            username = presence.account_name
            password = presence.password
            # сохраняем пользователя в базу если его там еще нет
            if not self.repo.client_exist(username):
                self.repo.add_client(username, password)
            if not self.repo.password_correct(username, password):
                response = JimResponse(WRONG_PASSWORD, error='Неверный пароль')
                return response.to_dict()

        except Exception as e:
            # шлем код ошибки
            response = JimResponse(WRONG_REQUEST, error=str(e))
            return response.to_dict()
        else:
            # всё ок
            response = JimResponse(OK)
            return response.to_dict()

    # def authenticate_response(self, authenticate_message):
    #     """Формирование ответа клиенту"""
    #     try:
    #         authenticate = Jim.from_dict(authenticate_message)
    #         username = authenticate.account_name
    #         password = authenticate.password
    #         # сохраняем пользователя в базу если его там еще нет
    #         if not self.repo.client_exist(username):
    #             self.repo.add_client(username, password)
    #         if not self.repo.password_correct(username, password):
    #             response = JimResponse(WRONG_PASSWORD, error='Неверный пароль')
    #             return response.to_dict()
    #
    #     except Exception as e:
    #         # шлем код ошибки
    #         response = JimResponse(WRONG_REQUEST, error=str(e))
    #         return response.to_dict()
    #     else:
    #         # всё ок
    #         response = JimResponse(OK)
    #         return response.to_dict()


class Server:
    """Класс сервера"""

    def __init__(self, handler):

        # обработчик событий
        self.handler = handler
        # список клиентов
        self.clients = []
        # сокет
        self.server = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP

    def bind(self, addr, port):
        # запоминаем адрес и порт
        self.server.bind((addr, port))

    def listen_forever(self):
        # запускаем цикл обработки событиц много клиентов
        self.server.listen(15)
        self.server.settimeout(0.2)

        while True:
            try:
                client, addr = self.server.accept()  # проверка подключений
                presense = get_message(client)
                response = self.handler.presense_response(presense)
                send_message(client, response)
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
                    # Ничего не делать, если какой-то клиент отключился
                    pass

                # Получаем входные сообщения
                requests = self.handler.read_requests(r, self.clients)
                # Выполняем отправку входящих сообщений
                self.handler.write_responses(requests, w, self.clients)


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

    handler = Handler()
    server = Server(handler)
    server.bind(addr, port)
    server.listen_forever()
