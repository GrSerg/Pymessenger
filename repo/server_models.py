import os
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Client(Base):
    """Клиент"""
    __tablename__ = 'Client'
    ClientId = Column(Integer, primary_key=True)
    Name = Column(String, unique=True)
    Password = Column(String)
    Info = Column(String, nullable=True)

    def __init__(self, name, password, info=None):
        self.Name = name
        self.Password = password
        if info:
            self.Info = info

    def __repr__(self):
        return "<Client ('%s', '%s')>" % (self.Name, self.Password)

    def __eq__(self, other):
        # Клиенты равны, если равны их имена
        return self.Name == other.Name


class ClientContact(Base):
    """Связка клиент-контакт для хранения списка контактов"""
    __tablename__ = 'ClientContact'
    # Первичный ключ
    ClientContactId = Column(Integer, primary_key=True)
    # id клиента
    ClientId = Column(Integer, ForeignKey('Client.ClientId'))
    # id контакта
    ContactId = Column(Integer, ForeignKey('Client.ClientId'))

    def __init__(self, client_id, contact_id):
        self.ClientId = client_id
        self.ContactId = contact_id


# путь до папки где лежит этот модуль
DB_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
# путь до папки с базой данных
DB_PATH = os.path.join(DB_FOLDER_PATH, 'server.db')
# создаем движок
engine = create_engine('sqlite:///{}'.format(DB_PATH), echo=False)
# Создание структуры базы данных
Base.metadata.create_all(engine)
# Создание сессии
Session = sessionmaker(bind=engine)
session = Session

session = session