#!/usr/bin/env python

import sys
from distutils.core import setup
from domain.helper import OS

requirements = [
    'pygubu', #==0.9.8.2
    'pyinstaller' #==3.4
]

if OS.is_linux:
    requirements.append('ttkthemes') #==2.1.0

setup(
    name='Templatizator',
    version='1.0',
    description='Application helper to create sets of files in projects',
    author='Jhonas Nascimento',
    author_email='jhonasn@gmail.com',
    url='https://github.com/jhonasn/templatizator',
    packages=[],
    requires=requirements
)
