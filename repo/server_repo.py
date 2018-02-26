from .server_models import Client, ClientContact
from .server_errors import ContactDoesNotExist


class Repo:
    """Серверное хранилище"""
    def __init__(self, session):
        # Запоминаем сессию, чтобы было удобно с ней работать
        self.session = session

    def add_client(self, username, info=None):
        """Добавление клиента"""
        new_item = Client(username, info)
        self.session.add(new_item)
        self.session.commit()

    def client_exist(self, username):
        """Проверка, что клиент уже есть"""
        result = self.session.query(Client).filter(Client.Name == username).count() > 0
        return result

    def get_client_by_username(self, username):
        """Получение клиента по имени"""
        client = self.session.query(Client).filter(Client.Name == username).first()
        return client

    def add_contact(self, client_username, contact_username):
        """Добавление контакта"""
        contact = self.get_client_by_username(contact_username)
        if contact:
            client = self.get_client_by_username(client_username)
            if client:
                cc = ClientContact(client_id=client.ClientId, contact_id=contact.ClientId)
                self.session.add(cc)
                self.session.commit()
            else:
                pass
        else:
            raise ContactDoesNotExist(contact_username)

    def del_contact(self, client_username, contact_username):
        """Удаление контакта"""
        contact = self.get_client_by_username(contact_username)
        if contact:
            client = self.get_client_by_username(client_username)
            if client:
                cc = self.session.query(ClientContact).filter(
                    ClientContact.ClientId == client.ClientId).filter(
                    ClientContact.ContactId == contact.ClientId).first()
                self.session.delete(cc)
            else:
                pass
        else:
            raise ContactDoesNotExist(contact_username)

    def get_contacts(self, client_username):
        """Получение контактов клиента"""
        client = self.get_client_by_username(client_username)
        result = []
        if client:
            contacts_clients = self.session.query(ClientContact).filter(ClientContact.ClientId == client.ClientId)
            for contact_client in contacts_clients:
                contact = self.session.query(Client).filter(client.ClientId == contact_client.ContactId).first()
                result.append(contact)
        return result

    def get_clients(self):
        """Получение всех клиентов"""
        return self.session.query(Client).all()