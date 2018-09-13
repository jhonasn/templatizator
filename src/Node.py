import os

class Node:
    def __init__(self, path, is_directory = True):
        self.path = path
        self.name = os.path.basename(path)
        self.is_directory = is_directory
        self.children = []
        self.parent = None

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def create_child(self, name):
        child = Node(os.path.join(self.path, name), False)
        self.add_child(child)
        return child

    def remove_child(self, child):
        self.children.remove(child)

    def remove(self):
        self.parent.remove_child(self)
        del self

    def find_node(self, path):
        if self.path == path:
            return self
        else:
            for c in self.children:
                if c.path == path:
                    return c
                elif len(c.children) > 0:
                    p = c.find_node(path)
                    if p != None:
                        return p
            return None

    def from_path(path):
        parent = Node(path)
        for root, directories, files in os.walk(path):
            node = parent.find_node(root)

            for directory in directories:
                path = os.path.join(root, directory)
                node.add_child(Node(path))

        return parent

    def get_name(self):
        return f'📂 {self.name}' if self.is_directory else f'⌹ {self.name}'

    def get_actions(self):
        return '+' if self.is_directory else '-'

    def print_node(self, tabs = ''):
        print(tabs + self.name if self.name else 'Parent')
        for c in self.children:
            if len(c.children) > 0:
                c.print_node(tabs + '\t')
            else:
                print(tabs + '\t' + c.name)

    def fill_treestore(self, store, parent_iter = None):
        if not parent_iter:
            parent_iter = store.append(None, [self.get_name(), self.get_actions(), self.path])

        for c in self.children:
            child_parent_iter = store.append(parent_iter, [c.get_name(), c.get_actions(), c.path])
            if len(c.children) > 0:
                c.fill_treestore(store, child_parent_iter)
