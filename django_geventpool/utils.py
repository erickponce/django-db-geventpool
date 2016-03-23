# coding=utf-8

from functools import wraps

from django.core.signals import request_finished
from django.db import close_old_connections


def close_connection(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        finally:
            request_finished.send(sender='greenlet')
    return wrapper
