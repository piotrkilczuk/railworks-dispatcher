#!/usr/bin/env python

from setuptools import setup


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: MIT License',
    'Operating System :: Microsoft :: Windows',
    'Programming Language :: Python',
    'Topic :: Games/Entertainment :: Simulation',
]


setup(
    name='Dispatcher',
    description='Creates a work order by choosing a random scenario from your Railworks folder.',
    classifiers=CLASSIFIERS,
    url='https://github.com/centralniak/railworks-dispatcher',
    author='Piotr Kilczuk',
    author_email='centralny@centralny.info',
    license='MIT License',

    version='0.4.11',
    platforms=['Windows', 'POSIX'],

    entry_points={
        'console_scripts': ['dispatcher=dispatcher:main'],
    },
    py_modules=['dispatcher'],
)
