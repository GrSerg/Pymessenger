import logging
import logging.handlers
import os

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
