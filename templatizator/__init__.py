#!/usr/bin/python3
'''Initialize the application'''
from sys import argv

# initiate only if not executing setup
if not any(filter(lambda arg: 'setup.py' in arg or 'pytest' in arg, argv)):
    from templatizator.presentation import initialize
    from templatizator.domain.container import Container

    Container.configure()
    initialize()
