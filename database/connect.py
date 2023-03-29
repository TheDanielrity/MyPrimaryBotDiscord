import sys 
from psycopg2 import pool as db
import logging as log
log.getLogger(__name__)
class Connection:
    _DATABASE = 'bknbpf8hqbsnco6wz5i7'
    _USERNAME = 'u2mb0wjb5ciuqwbw1ivk'
    _PASSWORD = 'J1hm7oFi6aenqbJ47DT1'
    _DB_PORT = '5432'
    _HOST = 'bknbpf8hqbsnco6wz5i7-postgresql.services.clever-cloud.com'
    _MIN_CON = 1
    _MAX_CON = 3
    _pool = None

    @classmethod
    def getPool(cls):
        if cls._pool is None:
            try:
                cls._pool = db.SimpleConnectionPool(cls._MIN_CON, cls._MAX_CON,
                                                    host = cls._HOST,
                                                    user = cls._USERNAME,
                                                    password = cls._PASSWORD,
                                                    port = cls._DB_PORT,
                                                    database = cls._DATABASE)
                return cls._pool

            except Exception as e:
                log.error(f'Ha ocurrido una excepción al iniciar el pool: {e}')
                sys.exit()
        else:
            return cls._pool

    @classmethod
    def getConnect(cls):
        try:
            connect = cls.getPool().getconn()
            return connect
        except Exception as e:
            log.error(f'Ha ocurrido una excepción al obtener una conexión del pool: {e}')
            sys.exit()

    @classmethod
    def freeConnect(cls, connect):
        try:
            cls.getPool().putconn(connect)
        except Exception as e:
            log.error(f'Ha ocurrido un error al liberar la conexión: {e}')
            sys.exit()
            
    @classmethod
    def closeConnects(cls):
        cls.getPool().closeall()


if __name__ == '__main__':
    """ conn = ConnectionMySQL.getConnect()
    cur = conn.cursor()
    cur.execute('SELECT * FROM guildInvites')
    data = cur.fetchall()
    
    conn = Connection.getConnect()
    cur = conn.cursor()
    cur.executemany('INSERT INTO guildInvites VALUES(%s, %s, %s, %s, %s, %s, %s)', data)
    conn.commit() """