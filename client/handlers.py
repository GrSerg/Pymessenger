from JIM.protocol import *
from PyQt5.QtCore import QObject, pyqtSignal


class Receiver:
    """Класс получатель информации из сокета"""
    def __init__(self, sock, request_queue):
        # запоминаем очередь ответов
        self.request_queue = request_queue
        # запоминаем сокет
        self.sock = sock
        self.is_alive = False

    def process_message(self, message):
        """метод для обработки принятого сообщения, будет переопределен в наследниах"""
        pass

    def poll(self):
        self.is_alive = True
        while True:
            if not self.is_alive:
                break
            data = get_message(self.sock)
            try:
                # преобразуем словарь в Jim, это может быть action или response
                jm = Jim.from_dict(data)
                # если это сообщение
                if isinstance(jm, JimMessage):
                    # обрабатываем
                    self.process_message(jm)
                else:
                    # Это либо ответ от сервера, либо действия с контактами
                    # складываем в очередь
                    self.request_queue.put(jm)
            except Exception as e:
                # Ошибки быть не должно, так как сервер должен отправлять верные данные
                # но лучше этот случай все равно обработать
                print(e)

    def stop(self):
        self.is_alive = False


class GuiReceiver(Receiver, QObject):
    """GUI обработчик входящих сообщений"""
    # наследуюем от QObject чтобы работала модель сигнал слот
    gotData = pyqtSignal(str)
    # событие (сигнал) что прием окончен
    finished = pyqtSignal(int)

    def __init__(self, sock, request_queue):
        # инициализируем как Receiver
        Receiver.__init__(self, sock, request_queue)
        # инициализируем как QObject
        QObject.__init__(self)

    def process_message(self, message):
        """Обработка сообщения"""
        # Генерируем сигнал (сообщаем, что произошло событие)
        # В скобках передаем нужные нам данные
        text = '{} >>> {}'.format(message.from_, message.message)
        self.gotData.emit(text)

    def poll(self):
        super().poll()
        # Когда обработка событий закончиться сообщаем об этом генерируем сигнал finished
        self.finished.emit(0)
