class ContactDoesNotExist(Exception):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'Контакт {} не существует'.format(self.name)
