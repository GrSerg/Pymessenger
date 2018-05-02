import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QThread, pyqtSlot

from client import Client
from handlers import GuiReceiver

# Получаем параметры скрипта
try:
    addr = sys.argv[1]
except IndexError:
    addr = 'localhost'
try:
    port = int(sys.argv[2])
except IndexError:
    port = 7777
except ValueError:
    print('Порт должен быть целым числом')
    sys.exit(0)
try:
    name = sys.argv[3]
    print(name)
except IndexError:
    name = 'GuiGuest'
try:
    password = sys.argv[3]
except IndexError:
    if name == 'GuiGuest':
        password = 'GuiGuest_pass1'
    else:
        raise Exception('Неверный пароль')


# Создаем приложение
app = QtWidgets.QApplication(sys.argv)
# грузим главную форму
window = uic.loadUi('main.ui')
# создаем клиента на запись
client = Client(name, password, addr, port)
# получаем список контактов с сервера, которые лежат у нас - не надежные
client.connect()
# contact_list = client.get_contacts()
# client.disconnect()
listener = GuiReceiver(client.sock, client.request_queue)


@pyqtSlot(str)
def update_chat(data):
    """Отображение сообщения в истории"""
    try:
        msg = data
        window.listWidgetMessages.addItem(msg)
    except Exception as e:
        print(e)


# сигнал мы берем из нашего GuiReciever
listener.gotData.connect(update_chat)

# Используем QThread так рекомендуется, но можно и обычный
# th_listen = threading.Thread(target=listener.poll)
# th_listen.daemon = True
# th_listen.start()
th = QThread()
listener.moveToThread(th)

# ---------- Важная часть - связывание сигналов и слотов ----------
# При запуске потока будет вызван метод search_text
th.started.connect(listener.poll)
th.start()

contact_list = client.get_contacts()


def load_contacts(contacts):
    """загрузка контактов в список"""
    # Чистим список
    window.listWidgetContacts.clear()
    # добавляем
    for contact in contacts:
        window.listWidgetContacts.addItem(contact)


# грузим контакты в список сразу при запуске приложения
load_contacts(contact_list)


def add_contact():
    """Добавление контакта"""
    try:
        # Получаем имя из QTextEdit
        username = window.textEditUsername.toPlainText()
        if username:
            # соединение
            # print(username)
            client.connect()
            # добавляем контакт - шлем запрос на сервер
            client.add_contact(username)
            # добавляем имя в QListWidget
            window.listWidgetContacts.addItem(username)
            # отключаемся
            client.disconnect()
    except Exception as e:
        print(e)


# Связываем сигнал нажатия кнопки добавить со слотом функцией добавить контакт
window.pushButtonAddContact.clicked.connect(add_contact)


def del_contact():
    """Удаление контакта"""
    try:
        # получаем выбранный элемент в QListWidget
        current_item = window.listWidgetContacts.currentItem()
        # получаем текст - это имя нашего контакта
        username = current_item.text()
        # удаление контакта (отправляем запрос на сервер)
        client.del_contact(username)
        # удаляем контакт из QListWidget
        current_item = window.listWidgetContacts.takeItem(window.listWidgetContacts.row(current_item))
        del current_item
    except Exception as e:
        print(e)


# связываем сигнал нажатия на кнопку и слот функцию удаления контакта
window.pushButtonDelContect.clicked.connect(del_contact)


# форматирование текста жирным
def action_bold():
    cursor = window.textEditMessage.textCursor()
    text = cursor.selectedText()
    window.textEditMessage.insertHtml('<b>%s</b>' % text)


# форматирование текста курсивом
def action_italic():
    cursor = window.textEditMessage.textCursor()
    text = cursor.selectedText()
    window.textEditMessage.insertHtml('<i>%s</i>' % text)


# форматирование текста подчеркиванием
def action_underlined():
    cursor = window.textEditMessage.textCursor()
    text = cursor.selectedText()
    window.textEditMessage.insertHtml('<u>%s</u>' % text)


# связываем сигнал нажатия на кнопку и слот функцию форматирования
window.pushButtonActionBold.clicked.connect(action_bold)
window.pushButtonActionItalic.clicked.connect(action_italic)
window.pushButtonActionUnderlined.clicked.connect(action_underlined)


# отправка сообщения
def send_message():
    text = window.textEditMessage.toPlainText()
    if text:
        # получаем выделенного пользователя
        selected_index = window.listWidgetContacts.currentIndex()
        # получаем имя пользователя
        user_name = selected_index.data()
        # отправляем сообщение
        client.send_message(user_name, text)
        # будем выводить то что мы отправили в общем чате
        msg = '{} >>> {}'.format(name, text)
        window.listWidgetMessages.addItem(msg)


# связываем сигнал нажатия на кнопку и слот функцию отправки сообщения
window.PushButtonSend.clicked.connect(send_message)


# def open_chat():
#     """Открытие модального чата (модальное для демонстрации)"""
#     # грузим QDialog чата
#     dialog = uic.loadUi('chat.ui')
#     # запускаем в модальном режиме
#     dialog.exec()
#
# # Пока мы не можем передать элемент на который нажали - сделать в следующий раз через наследование
# window.listWidgetContacts.itemDoubleClicked.connect(open_chat)

# рисуем окно
window.show()
# точка запуска приложения
sys.exit(app.exec_())
