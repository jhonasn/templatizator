#!/usr/bin/python3
'''Initialize the application'''
from templatizator.presentation import initialize
from templatizator.domain.container import Container
from templatizator.domain.helper import OS

Container.configure()
initialize()
