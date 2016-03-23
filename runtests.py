#!/usr/bin/env python
import sys
# from django.db import connections

import gevent.monkey
gevent.monkey.patch_all()

import psycogreen.gevent
psycogreen.gevent.patch_psycopg()

import django
from django.conf import settings


if django.VERSION < (1, 6):
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django_db_geventpool.backends.postgresql_psycopg2',
                'NAME': 'test',
                'USER': 'postgres',
                'PASSWORD': 'postgres',
                'OPTIONS': {'autocommit': True},
            }
        },
        INSTALLED_APPS=(
            'django_db_geventpool',
            'tests',
        ),
        USE_TZ=True,
    )
else:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django_geventpool.backends.postgresql_psycopg2',
                'HOST': 'dntdevserver2',
                'NAME': 'test_django_geventpool',
                'USER': 'karoo',
                'PASSWORD': 'k8EJB4Sm',
                'ATOMIC_REQUESTS': False,
                'CONN_MAX_AGE': 0,
                'OPTIONS': {
                    'MAX_CONNS': 5
                }
            }
        },
        INSTALLED_APPS=(
            'tests',
            'django_geventpool',
        ),
        USE_TZ=True,
        MIDDLEWARE_CLASSES = (
            # 'django.middleware.transaction.TransactionMiddleware'
        ),
    )
    try:
        django.setup()
    except AttributeError:
        pass  # not using django 1.7


try:
    from django.test.runner import DiscoverRunner as TestSuiteRunner
except ImportError:  # DiscoverRunner is the preferred one for django > 1.7
    from django.test.simple import DjangoTestSuiteRunner as TestSuiteRunner

# connections['default'].allow_thread_sharing = True

test_runner = TestSuiteRunner(verbosity=1)

try:
    failures = test_runner.run_tests(['tests', ])
    if failures:
        sys.exit(failures)

    # from tests.tests import test_multiple_connections
    # greenlets = []
    #
    # for x in range(0, 5):
    #     greenlets.append(gevent.spawn(test_multiple_connections, x))
    # gevent.joinall(greenlets)
    # for i in range(0, 10):
    #     gevent.sleep(1)

except Exception as e:
    print e
    print 'Finished with errors!'
    sys.exit()
