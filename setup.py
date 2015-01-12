#!/usr/bin/env python

import os

from setuptools import setup


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: MIT License',
    'Operating System :: Microsoft :: Windows',
    'Programming Language :: Python',
    'Topic :: Games/Entertainment :: Simulation',
]


def compile_js():
    setup_folder = os.path.abspath(os.path.dirname(__file__))
    jar_location = os.path.join(setup_folder, 'build_tools', 'compiler.jar')
    source_location = os.path.join(setup_folder, 'Dispatcher', '*.js')
    target_location = os.path.join(setup_folder, 'Dispatcher', 'Artwork', 'build.js')
    # @TODO: probably will require different redirections on Windows
    os.system('java -jar %s %s > %s 2> /dev/null' % (jar_location, source_location, target_location))

compile_js()


setup(
    name='Dispatcher',
    description='Creates a work order by choosing a random scenario from your Railworks folder.',
    classifiers=CLASSIFIERS,
    url='https://github.com/centralniak/railworks-dispatcher',
    author='Piotr Kilczuk',
    author_email='centralny@centralny.info',
    license='MIT License',

    version='0.4.15',
    install_requires=['PyYAML'],
    platforms=['Windows', 'POSIX'],

    entry_points={
        'console_scripts': ['dispatcher=dispatcher:main'],
    },
    py_modules=['dispatcher'],
)
