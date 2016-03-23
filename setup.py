# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='django-geventpool',
    version='1.2.1',
    install_requires=[
        'django>=1.5',
        'psycopg2>=2.5.1',
        'psycogreen>=1.0'],
    url='https://github.com/erickponce/django-db-geventpool',
    description='Add a DB connection pool using gevent to django (based on django-db-geventpool)',
    long_description=open("README.rst").read(),
    packages=find_packages(),
    include_package_data=True,
    license='Apache 2.0',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    author='Erick Ponce Leão',
    author_email='erickponceleao@gmail.com'
)
