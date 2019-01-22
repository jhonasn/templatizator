#!/usr/bin/python3
'''Initialize the application'''
from presentation.start import initialize
from domain.container import Container
from domain.helper import OS

OS.set_current_directory()

Container.configure()
initialize()
