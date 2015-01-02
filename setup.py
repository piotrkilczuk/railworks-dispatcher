#!/usr/bin/env python

from setuptools import setup


setup(
    name='Dispatcher',
    description='Creates a work order by choosing a random scenario from your Railworks folder.',
    url='https://github.com/centralniak/railworks-dispatcher',
    author='Piotr Kilczuk',
    author_email='centralny@centralny.info',

    version='0.9.0',

    entry_points={
        'console_scripts': ['dispatcher=dispatcher:main'],
    },
    py_modules=['dispatcher'],
)
