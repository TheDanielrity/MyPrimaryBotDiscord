from database.connect import Connection
import logging as log
log.getLogger(__name__)

class Cursor:

    def __init__(self):
        self._connect = None
        self._cursor = None

    def __enter__(self):
        self._connect = Connection.getConnect()
        self._cursor = self._connect.cursor()
        return self._cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self._connect.rollback()
            log.error(f'Ocurrió una excepción {exc_type} {exc_tb}')
        else:
            self._connect.commit()
        self._cursor.close()
        Connection.freeConnect(self._connect)


if __name__ == '__main__':
    pass