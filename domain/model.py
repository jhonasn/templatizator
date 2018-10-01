#import os
#from copy import copy

class Node:
    # node from a graph/node tree
    def __init__(self, path):
        self.path = path
        self.children = []
        self.parent = None

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def remove_child(self, child):
        self.children.remove(child)

    def remove(self):
        self.parent.remove_child(self)
        del self

class Directory(Node):
    # directory from a file tree
    def __init__(self, path, opened = False):
        super(path)
        self.open = opened

class File(Node):
    # file from a file tree
    pass

class Template(File):
    # template file
    pass

class ConfigurableFile(File):
    # configurable file like xml or json or another
    # that receives template files
    pass

class Project(Directory):
    pass

class Configuration(Directory):
    pass

class Variable:
    def __init__(self, key, value):
        self.key = key
        self.value = value

