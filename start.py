#!/usr/bin/python3
'''Initialize the application'''
from presentation.start import initialize
from domain.container import Container

Container.configure()
initialize()
