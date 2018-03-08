import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from client import Client


# Создаем приложение
app = QtWidgets.QApplication(sys.argv)
# грузим главную форму
window = uic.loadUi('main.ui')
# создаем клиента на запись
client = Client(login='Serg')
# получаем список контактов с сервера, которые лежат у нас - не надежные
client.connect()
contact_list = client.get_contacts()
client.disconnect()

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
        # соединение
        client.connect()
        # удаление контакта (отправляем запрос на сервер)
        client.del_contact(username)
        # отключаемся
        client.disconnect()
        # удаляем контакт из QListWidget
        current_item = window.listWidgetContacts.takeItem(window.listWidgetContacts.row(current_item))
        del current_item
    except Exception as e:
        print(e)

# связываем сигнал нажатия на кнопку и слот функцию удаления контакта
window.pushButtonDelContect.clicked.connect(del_contact)


def open_chat():
    """Открытие модального чата (модальное для демонстрации)"""
    # грузим QDialog чата
    dialog = uic.loadUi('chat.ui')
    # запускаем в модальном режиме
    dialog.exec()


# Пока мы не можем передать элемент на который нажали - сделать в следующий раз через наследование
window.listWidgetContacts.itemDoubleClicked.connect(open_chat)

# Контекстное меню при нажатии правой кнопки мыши (пока тестовый вариант для демонстрации)
# Создаем на листе
window.listWidgetContacts.setContextMenuPolicy(Qt.CustomContextMenu)
window.listWidgetContacts.setContextMenuPolicy(Qt.ActionsContextMenu)
quitAction = QtWidgets.QAction("Quit", None)
quitAction.triggered.connect(app.quit)
window.listWidgetContacts.addAction(quitAction)

# рисуем окно
window.show()
# точка запуска приложения
sys.exit(app.exec_())
