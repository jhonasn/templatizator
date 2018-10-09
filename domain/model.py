'''Model set module'''
from abc import ABC, abstractmethod


# Just one method contract required
# pylint: disable=too-few-public-methods
class Serializable(ABC):
    '''Base class for serializable classes (all models must be)'''
    @abstractmethod
    def serialize(self):
        '''Contract method to serialize object'''
        raise NotImplementedError('Object serialize method not implemented')


class Node(Serializable):
    '''Base class for node graph.
    Commonly used as a file tree in this project
    '''
    def __init__(self, path=None, name=None):
        self.path = path
        self.name = name
        self.children = []
        self.parent = None

    def add_child(self, child):
        '''Add child to this node and set parent to the child'''
        self.children.append(child)
        child.parent = self

    def remove_child(self, child):
        '''Remove child from this node'''
        self.children.remove(child)

    def remove(self):
        '''Remove itself from its parent'''
        self.parent.remove_child(self)
        del self

    def serialize(self):
        '''Serialize relevant node attributes'''
        return {'path': self.path}


class Directory(Node):
    '''Represents a directory into a file tree'''
    def __init__(self, path=None, name=None, opened=False):
        super().__init__(path, name)
        self.open = opened

    def serialize(self):
        '''Serialize relevant attributes'''
        obj = super().serialize()
        obj['open'] = self.open
        return obj


class File(Node):
    '''Represents a file into a file tree'''
    pass


class Template(File):
    '''Represents a template file into a file tree'''
    pass


class ConfigurableFile(File):
    '''Represents a configurable file into a file tree.
    Samples of configurables files can be xml or json files but any file can be
    a configurable, the configurable will receive the templates in placeholders
    in any way desired through the placeholder template lines
    '''
    def __init__(self, path=None, name=None, expression=None, after=True):
        super().__init__(path, name)
        self.expression = expression
        self.after = after

    def serialize(self):
        '''Serialize relevant attributes'''
        obj = super().serialize()
        obj['expression'] = self.expression
        obj['after'] = self.after
        return obj


class Project(Directory):
    '''Represents the project directory into the file tree'''
    def __init__(self, path=None, name=None, path_name=None, selected=False):
        super().__init__(path, name, True)
        # friendly project name
        self.path_name = path_name
        self.selected = selected

    def serialize(self):
        '''Serialize relevant attributes'''
        obj = super().serialize()
        del obj['open']
        obj['path_name'] = self.path_name
        obj['selected'] = self.selected
        return obj


class Variable(Serializable):
    '''Project variables that will be replacing placeholders in file names
    or file contents
    '''
    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value

    def serialize(self):
        '''Serialize relevant attributes'''
        return {'name': self.name, 'value': self.value}
