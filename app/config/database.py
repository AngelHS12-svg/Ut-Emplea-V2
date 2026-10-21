import os
from threading import Lock

from flask import current_app, g, has_request_context
from psycopg2 import pool

_pool = None
_pool_lock = Lock()

def connection_options():
    options = {'connect_timeout': 5, 'client_encoding': 'utf8'}
    if os.environ.get('DATABASE_URL'):
        options['dsn'] = os.environ['DATABASE_URL']
    else:
        options.update(
            host=os.environ.get('DB_HOST', 'db'), database=os.environ['DB_NAME'],
            user=os.environ['DB_USER'], password=os.environ['DB_PASSWORD'],
            port=os.environ.get('DB_PORT', '5432'),
        )
    return options

class ConnectionWrapper:
    def __init__(self, connection, pool_instance):
        self._connection = connection
        self._pool = pool_instance
        self._released = False

    def __getattr__(self, name):
        return getattr(self._connection, name)

    def close(self):
        if self._released:
            return
        self._released = True
        discard = bool(self._connection.closed)
        if not discard:
            try:
                self._connection.rollback()
            except Exception:
                discard = True
        try:
            self._pool.putconn(self._connection, close=discard)
        except Exception:
            self._connection.close()
            raise

def get_connection():
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                maximum = int(os.environ.get('DB_POOL_MAX', '10'))
                if maximum < 1:
                    raise ValueError('DB_POOL_MAX debe ser positivo.')
                _pool = pool.ThreadedConnectionPool(1, maximum, **connection_options())
    # No se abren conexiones adicionales al agotarse el pool.
    connection = ConnectionWrapper(_pool.getconn(), _pool)
    if has_request_context():
        g.setdefault('_db_connections', []).append(connection)
    return connection


def close_request_connections(error=None):
    for connection in g.pop('_db_connections', []):
        try:
            connection.close()
        except Exception:
            current_app.logger.exception('No se pudo devolver una conexión al pool')
