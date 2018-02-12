import logging
import logging.handlers
import os
from functools import wraps


class Log:
    """Класс декоратор для логирования функций"""

    def __init__(self, logger):
        # запоминаем логгер, чтобы можно было использовать разные
        self.logger = logger

    @staticmethod
    def _create_message(result=None, *args, **kwargs):
        """Формирует сообщение для записи в лог"""
        message = ''
        if args:
            message += 'args: {} '.format(args)
        if kwargs:
            message += 'kwargs: {} '.format(kwargs)
        if result:
            message += '= {}'.format(result)
        # Возвращаем итоговое сообщение
        return message

    def __call__(self, func):
        """Определяем __call__ для возможности вызова экземпляра как декоратора"""

        @wraps(func)
        def decorated(*args, **kwargs):
            # Выполняем функцию и получаем результат
            result = func(*args, **kwargs)
            # Формируем сообщение в лог
            message = Log._create_message(result, *args, **kwargs)
            # Пишем сообщение в лог
            # Хотя мы и подменили с помощью wraps имя и модуль для внутренней функции,
            # логгер всё равно берет не те, поэтому приходиться делать через decorated.__name__, !
            self.logger.info('{} - {} - {}'.format(message, decorated.__name__, decorated.__module__))
            return result

        return decorated


# путь к папке с логами
LOG_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
# формат сообщений в логе
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# настройка логгера сервера
SERVER_LOG_FILE_PATH = os.path.join(LOG_FOLDER_PATH, 'server.log')
server_logger = logging.getLogger('server')
server_handler = logging.handlers.TimedRotatingFileHandler(SERVER_LOG_FILE_PATH, when='d')
server_handler.setFormatter(formatter)
server_logger.addHandler(server_handler)
server_logger.setLevel(logging.INFO)

# настройка логгера клиента
CLIENT_LOG_FILE_PATH = os.path.join(LOG_FOLDER_PATH, 'client.log')
client_logger = logging.getLogger('client')
client_handler = logging.FileHandler(CLIENT_LOG_FILE_PATH, encoding='utf-8')
client_handler.setFormatter(formatter)
client_logger.addHandler(client_handler)
client_logger.setLevel(logging.INFO)
