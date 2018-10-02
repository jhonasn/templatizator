from abc import ABC, abstractmethod

class Serializable(ABC):
    @abstractmethod
    def serialize(self):
        raise NotImplementedError('Object serialize method not implemented')

class Node(Serializable):
    # node from a graph/node tree
    def __init__(self, path = None):
        self.path = path
        self.children = []
        self.parent = None

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def create_child(self, name):
        child = Node(os.path.join(self.path, name))
        self.add_child(child)
        return child

    def remove_child(self, child):
        self.children.remove(child)

    def remove(self):
        self.parent.remove_child(self)
        del self

    def serialize(self):
        return { 'path': self.path }

class Directory(Node):
    # directory from a file tree
    def __init__(self, path = None, opened = False):
        super().__init__(path)
        self.open = opened

    def serialize(self):
        obj = super().serialize()
        obj['open'] = self.open
        return obj

class File(Node):
    # file from a file tree
    pass

class Template(File):
    # template file
    pass

class ConfigurableFile(File):
    # configurable file like xml or json or another
    # that receives template files
    def __init__(self, path = None, expression = None, after = True):
        super().__init__(path)
        self.expression = expression
        self.after = after

    def serialize(self):
        obj = super().serialize()
        obj['expression'] = self.expression
        obj['after'] = self.after
        return obj

class Project(Directory):
    def __init__(self, path = None, name = None, selected = False):
        super().__init__(path, True)
        # friendly project name
        self.name = name
        self.selected = selected

    def serialize(self):
        obj = super().serialize()
        obj['name'] = self.name
        obj['selected'] = self.selected
        return obj

class Variable(Serializable):
    def __init__(self, key = None, value = None):
        self.key = key
        self.value = value

    def serialize(self):
        return { 'key': self.key, 'value': self.value }

