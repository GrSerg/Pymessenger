import json
import time as ctime

# Константы для работы JIM протокола

# Ключи
ACTION = 'action'
USER = 'user'
ACCOUNT_NAME = 'account_name'
USER_ID = 'user_id'
RESPONSE = 'response'
TIME = 'time'
ERROR = 'error'
ALERT = 'alert'
QUANTITY = 'quantity'

# Значения
PRESENCE = 'presence'
MSG = 'msg'
TO = 'to'
FROM = 'from'
MESSAGE = 'message'
GET_CONTACTS = 'get_contacts'
CONTACT_LIST = 'contact_list'
ADD_CONTACT = 'add_contact'
DEL_CONTACT = 'del_contact'

# Кортеж возможных действий
ACTIONS = (PRESENCE, MSG, GET_CONTACTS, CONTACT_LIST, ADD_CONTACT, DEL_CONTACT)

# Коды ответов (будут дополняться)
BASIC_NOTICE = 100
OK = 200
ACCEPTED = 202
WRONG_REQUEST = 400  # неправильный запрос/json объект
SERVER_ERROR = 500

# Кортеж из кодов ответов
RESPONSE_CODES = (BASIC_NOTICE, OK, ACCEPTED, WRONG_REQUEST, SERVER_ERROR)


USERNAME_MAX_LENGTH = 25
MESSAGE_MAX_LENGTH = 500

#############################
# Функции для сообщений


def dict_to_bytes(message_dict):
    """Преобразование словаря в байты"""
    # Проверям, что пришел словарь
    if isinstance(message_dict, dict):
        # Преобразуем словарь в json
        jmessage = json.dumps(message_dict)
        # Переводим json в байты
        bmessage = jmessage.encode()
        # Возвращаем байты
        return bmessage
    else:
        raise TypeError


def bytes_to_dict(message_bytes):
    """Получение словаря из байтов"""
    # Если переданы байты
    if isinstance(message_bytes, bytes):
        # Декодируем
        jmessage = message_bytes.decode()
        # Из json делаем словарь
        message = json.loads(jmessage)
        # Если там был словарь
        if isinstance(message, dict):
            # Возвращаем сообщение
            return message
        else:
            # Нам прислали неверный тип
            raise TypeError
    else:
        # Передан неверный тип
        raise TypeError


def send_message(sock, message):
    """Отправка сообщения"""
    # Словарь переводим в байты
    bprescence = dict_to_bytes(message)
    # Отправляем
    sock.send(bprescence)


def get_message(sock):
    """Получение сообщения"""
    # Получаем байты
    bresponse = sock.recv(1024)
    # переводим байты в словарь
    response = bytes_to_dict(bresponse)
    # возвращаем словарь
    return response

#############################
# Ошибки


class WrongInputError(Exception):
    pass


class WrongParamsError(WrongInputError):
    """Неверные параметры для действия"""

    def __init__(self, params):
        self.params = params

    def __str__(self):
        return 'Неверные параметры действий: {}'.format(self.params)


class WrongActionError(WrongInputError):
    """Когда передано неверное действие"""

    def __init__(self, action):
        self.action = action

    def __str__(self):
        return 'Неверное действие: {}'.format(self.action)


class WrongDictError(WrongInputError):
    """Когда пришел неправильный словарь"""

    def __init__(self, dict_name):
        self.dict_name = dict_name

    def __str__(self):
        return 'Неправильный словарь: {}'.format(self.dict_name)


class ToLongError(Exception):
    """Ошибка, когда поле длиннее чем нужно"""

    def __init__(self, name, value, max_length):
        self.name = name
        self.value = value
        self.max_length = max_length

    def __str__(self):
        return '{}: {} длиннее чем (> {} символов)'.format(self.name, self.value, self.max_length)


class ResponseCodeError(Exception):
    """Ошибка, когда неверный код ответа сервера"""
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return 'Неверный код ответа сервера: {}'.format(self.code)

#####################################
# Дескрипторы


class MaxLengthField:
    """Дескриптор ограничивающий размер поля"""

    def __init__(self, name, max_length):
        self.name = '_' + name
        self.max_lenght = max_length

    def __set__(self, instance, value):
        # если длина поля больше максимального значения
        if len(value) > self.max_lenght:
            # вызываем ошибку
            raise ToLongError(self.name, value, self.max_lenght)
        # иначе записываем данные в поле
        setattr(instance, self.name, value)

    def __get__(self, instance, owner):
        # получаем данные поля
        return getattr(instance, self.name)


class ResponseField:
    """Дескриптор правильных кодов ответов сервера"""

    def __init__(self, name):
        self.name = '_' + name

    def __set__(self, instance, value):
        # если значение кода не входит в список доступных кодов
        if value not in RESPONSE_CODES:
            # вызываем ошибку
            raise ResponseCodeError(value)
        # иначе записываем данные в поле
        setattr(instance, self.name, value)

    def __get__(self, instance, owner):
        # получаем данные поля
        return getattr(instance, self.name)


############################
# Классы протокола Jim

class Jim:

    def to_dict(self):
        return {}

    @staticmethod
    def try_create(jim_class, input_dict):
        try:
            return jim_class(**input_dict)
        except KeyError:
            raise WrongParamsError(input_dict)

    @staticmethod
    def from_dict(input_dict):
        """Наиболее важный метод создания объекта из входного словаря"""
        # должно быть action или response
        # если action
        if ACTION in input_dict:
            # достаем действие
            action = input_dict.pop(ACTION)
            # действие должно быть в списке действий
            if action in ACTIONS:
                if action == PRESENCE:
                    return Jim.try_create(JimPresense, input_dict)
                elif action == GET_CONTACTS:
                    return Jim.try_create(JimGetContacts, input_dict)
                elif action == CONTACT_LIST:
                    return Jim.try_create(JimContactList, input_dict)
                elif action == ADD_CONTACT:
                    return Jim.try_create(JimAddContact, input_dict)
                elif action == DEL_CONTACT:
                    return Jim.try_create(JimDelContact, input_dict)
                elif action == MSG:
                    try:
                        input_dict['from_'] = input_dict['from']
                    except KeyError:
                        raise WrongParamsError(input_dict)
                    del input_dict['from']
                    return Jim.try_create(JimMessage, input_dict)
            else:
                raise WrongActionError(action)
        elif RESPONSE in input_dict:
            return Jim.try_create(JimResponse, input_dict)
        else:
            raise WrongDictError(input_dict)


class JimAction(Jim):

    def __init__(self, action, time=None):
        self.action = action
        if time:
            self.time = time
        else:
            self.time = ctime.time()

    def to_dict(self):
        result = super().to_dict()
        result[ACTION] = self.action
        result[TIME] = self.time
        return result


class JimAddContact(JimAction):
    # Имя пользователя ограничено 25 символов - используем дескриптор
    account_name = MaxLengthField('account_name', USERNAME_MAX_LENGTH)
    # Имя пользователя ограничено 25 символов - используем дескриптор
    user_id = MaxLengthField('user_id', USERNAME_MAX_LENGTH)

    def __init__(self, account_name, user_id, time=None):
        self.account_name = account_name
        self.user_id = user_id
        super().__init__(ADD_CONTACT, time)

    def to_dict(self):
        result = super().to_dict()
        result[ACCOUNT_NAME] = self.account_name
        result[USER_ID] = self.user_id
        return result


class JimDelContact(JimAction):
    # Имя пользователя ограничено 25 символов - используем дескриптор
    account_name = MaxLengthField('account_name', USERNAME_MAX_LENGTH)
    # Имя пользователя ограничено 25 символов - используем дескриптор
    user_id = MaxLengthField('user_id', USERNAME_MAX_LENGTH)

    def __init__(self, account_name, user_id, time=None):
        self.account_name = account_name
        self.user_id = user_id
        super().__init__(DEL_CONTACT, time)

    def to_dict(self):
        result = super().to_dict()
        result[ACCOUNT_NAME] = self.account_name
        result[USER_ID] = self.user_id
        return result


class JimContactList(JimAction):
    # Имя пользователя ограничено 25 символов - используем дескриптор
    user_id = MaxLengthField('user_id', USERNAME_MAX_LENGTH)

    def __init__(self, user_id, time=None):
        self.user_id = user_id
        super().__init__(CONTACT_LIST, time)

    def to_dict(self):
        result = super().to_dict()
        result[USER_ID] = self.user_id
        return result


class JimGetContacts(JimAction):
    # Имя пользователя ограничено 25 символов - используем дескриптор
    account_name = MaxLengthField('account_name', USERNAME_MAX_LENGTH)

    def __init__(self, account_name, time=None):
        self.account_name = account_name
        super().__init__(GET_CONTACTS, time)

    def to_dict(self):
        result = super().to_dict()
        result[ACCOUNT_NAME] = self.account_name
        return result


class JimPresense(JimAction):
    # Имя пользователя ограничено 25 символов - используем дескриптор
    account_name = MaxLengthField('account_name', USERNAME_MAX_LENGTH)

    def __init__(self, account_name, time=None):
        self.account_name = account_name
        super().__init__(GET_CONTACTS, time)

    def to_dict(self):
        result = super().to_dict()
        result[ACCOUNT_NAME] = self.account_name
        return result


class JimMessage(JimAction):
    to = MaxLengthField('to', USERNAME_MAX_LENGTH)
    from_ = MaxLengthField('from', USERNAME_MAX_LENGTH)
    message = MaxLengthField('message', MESSAGE_MAX_LENGTH)

    def __init__(self, to, from_, message, time=None):
        self.to = to
        self.from_ = from_
        self.message = message
        super().__init__(MSG, time=time)

    def to_dict(self):
        result = super().to_dict()
        result[TO] = self.to
        result[FROM] = self.from_
        result[MESSAGE] = self.message
        return result


class JimResponse(Jim):
    # Используем дескриптор для поля ответ от сервера
    response = ResponseField('response')

    def __init__(self, response, error=None, alert=None, quantity=None):
        self.response = response
        self.error = error
        self.alert = alert
        self.quantity = quantity

    def to_dict(self):
        result = super().to_dict()
        result[RESPONSE] = self.response
        if self.error is not None:
            result[ERROR] = self.error
        if self.alert is not None:
            result[ALERT] = self.alert
        if self.quantity is not None:
            result[QUANTITY] = self.quantity
        return result