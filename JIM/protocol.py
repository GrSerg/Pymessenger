import json

'''Константы для работы JIM протокола'''

# Возможные ключи в сообщениях от клиентов
PRESENCE = 'presence'
MSG = 'msg'
QUIT = 'quit'

# Кортеж возможных действий (будет дополняться)
ACTIONS = (PRESENCE, MSG, QUIT)

# Обязательные ключи в сообщениях от клиента
ACTION = 'action'
TIME = 'time'

# Кортеж из обязательных ключей для сообщений от клиента
MANDATORY_MESSAGE_KEYS = (ACTION, TIME)

# Обязательные ключи в ответах сервера
RESPONSE = 'response'
TIME = 'time'

# Кортеж обязательных ключей в ответах от сервера
MANDATORY_RESPONSE_KEYS = (RESPONSE, TIME)

# Коды ответов (будут дополняться)
BASIC_NOTICE = 100
OK = 200
ACCEPTED = 202
WRONG_REQUEST = 400  # неправильный запрос/json объект
SERVER_ERROR = 500

# Кортеж из кодов ответов
RESPONSE_CODES = (BASIC_NOTICE, OK, ACCEPTED, WRONG_REQUEST, SERVER_ERROR)


class MandatoryKeyError(Exception):
    """Ошибка отсутствия обязательного ключа в сообщении"""

    def __init__(self, key):
        """
        :param key: обязательный ключ, которого нет в сообщении
        """
        self.key = key

    def __str__(self):
        return 'Не хватает обязательного атрибута {}'.format(self.key)


class ResponseCodeError(Exception):
    """Ошибка неверный код ответа от сервера"""

    def __init__(self, code):
        """
        :param code: Неверный код ответа
        """
        self.code = code

    def __str__(self):
        return 'Неверный код ответа {}'.format(self.code)


class ResponseCodeLenError(ResponseCodeError):
    """Ошибка неверная длина кода ответа, должна быть 3 символа"""

    def __str__(self):
        return 'Неверная длина кода {}. Длина кода должна быть 3 символа.'.format(self.code)


class BaseJimMessage:
    """Базовое сообщение для Jim протокола"""

    def __init__(self, **kwargs):

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __bytes__(self):
        """Возможность приводить сообщение сразу в байты bytes(jim_message)"""
        # Преобразуем в json
        message_json = json.dumps(self.__dict__)
        # Преобразуем в байты
        message_bytes = message_json.encode()
        return message_bytes

    @classmethod
    def create_from_bytes(cls, message_bytes):
        """Возможность создавать сообщение по набору байт"""
        # Байты в json
        message_json = message_bytes.decode()
        # json в словарь
        message_dict = json.loads(message_json)
        return cls(**message_dict)

    def __str__(self):
        return str(self.__dict__)


class JimMessage(BaseJimMessage):
    """Клиентское сообщение"""

    def __init__(self, **kwargs):
        # проверки
        if ACTION not in kwargs:
            raise MandatoryKeyError(ACTION)
        if TIME not in kwargs:
            raise MandatoryKeyError(TIME)
        super().__init__(**kwargs)


class JimResponse(BaseJimMessage):
    """Ответ сервера"""
    def __init__(self, **kwargs):
        # проверки
        if RESPONSE not in kwargs:
            raise MandatoryKeyError(RESPONSE)
        if TIME not in kwargs:
            raise MandatoryKeyError(TIME)
        code = kwargs[RESPONSE]
        if len(code) != 3:
            raise ResponseCodeLenError(code)
        if code not in RESPONSE_CODES:
            raise ResponseCodeError(code)
        super().__init__(**kwargs)