import datetime
import os
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Client(Base):
    """Клиент"""
    __tablename__ = 'Client'
    ClientId = Column(Integer, primary_key=True)
    Name = Column(String, unique=True)
    Info = Column(String, nullable=True)

    def __init__(self, name, info=None):
        self.Name = name
        if info:
            self.Info = info

    def __repr__(self):
        return "<Client ('%s')>" % self.Name

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



