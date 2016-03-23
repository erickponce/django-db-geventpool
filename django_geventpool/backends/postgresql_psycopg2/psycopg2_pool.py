# coding=utf-8

# this file is a modified version of the psycopg2 used at gevent examples
# to be compatible with django, also checks if
# DB connection is closed and reopen it:
# https://github.com/surfly/gevent/blob/master/examples/psycopg2_pool.py
import logging
import sys
import time
import exception
import copy

logger = logging.getLogger('django')

try:
    from gevent import queue
except ImportError:
    from eventlet import queue

from psycopg2 import connect, DatabaseError


if sys.version_info[0] >= 3:
    integer_types = int,
else:
    import __builtin__
    integer_types = int, __builtin__.long


class DatabaseConnectionPool(object):
    maxsize = None
    conn_idle_timeout = None
    conn_wait_timeout = None

    def __init__(self, maxsize, conn_idle_timeout, conn_wait_timeout):
        if not isinstance(maxsize, integer_types):
            raise TypeError('Expected integer, got %r' % (maxsize,))

        self.maxsize = maxsize
        self.conn_idle_timeout = conn_idle_timeout
        self.conn_wait_timeout = conn_wait_timeout

        self.pool = queue.Queue(maxsize=maxsize)
        self.used_conns = {}
        self.size = 0

    def get(self):
        try:
            pool = self.pool
            if self.size >= self.maxsize or pool.qsize() > 0:
                if not self.conn_wait_timeout and not pool.qsize():
                    raise exception.ConnPoolExhaustedError()

                new_item = pool.get(block=True, timeout=self.conn_wait_timeout)
                try:
                    # check connection is still valid
                    self.check_usable(new_item)
                    logger.debug("DB connection reused")
                except DatabaseError:
                    logger.debug("DB connection was closed, creating new one")
                    new_item = self.create_connection()
                self.tick_conn(new_item)
                return new_item
            else:
                self.size += 1
                try:
                    new_item = self.create_connection()
                    logger.debug("DB connection created")
                except:
                    self.size -= 1
                    raise
                self.tick_conn(new_item)
                return new_item
        except queue.Empty:
            raise exception.ConnWaitTimeoutError('Timeout waiting for connection.')

    def put(self, item):
        try:
            self.pool.put(item, timeout=2)
            self.conn_gc()
        except queue.Full:
            item.close()

    def tick_conn(self, conn):
        self.used_conns[id(conn)] = time.time()

    def conn_gc(self):
        if not self.conn_idle_timeout or self.pool.qsize() < 2:
            return
        now = time.time()
        used_conns = copy.copy(self.used_conns)
        for conn_id, last_used in used_conns.iteritems():
            try:
                expired = int(now - last_used) >= self.conn_idle_timeout
                if expired:
                    conn = self.pool.get(conn_id)
                    conn.close()
                    self.size -= 1
            except:
                pass

    def closeall(self):
        while not self.pool.empty():
            conn = self.pool.get_nowait()
            try:
                conn.close()
            except:
                pass
        self.size = 0


class PostgresConnectionPool(DatabaseConnectionPool):
    def __init__(self, *args, **kwargs):
        self.connect = kwargs.pop('connect', connect)
        self.connection = None
        maxsize = kwargs.pop('MAX_CONNS', 5)
        conn_idle_timeout = kwargs.pop('CONN_IDLE_TIMEOUT', 180)
        conn_wait_timeout = kwargs.pop('CONN_WAIT_TIMEOUT', 15)

        self.args = args
        self.kwargs = kwargs
        DatabaseConnectionPool.__init__(
            self, maxsize, conn_idle_timeout,
            conn_wait_timeout
        )

    def create_connection(self):
        conn = self.connect(*self.args, **self.kwargs)
        # set correct encoding
        conn.set_client_encoding('UTF8')
        return conn

    def check_usable(self, connection):
        connection.cursor().execute('SELECT 1')

