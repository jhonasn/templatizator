class Node:
    # node from a graph/node tree
    def __init__(self, path):
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

class Project:
    def __init__(self, name, path, selected = False):
        # friendly project name
        self.name = name
        # project path
        self.path = path
        self.selected = selected

class Variable:
    def __init__(self, key, value):
        self.key = key
        self.value = value

