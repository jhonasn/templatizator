import os

class Node:
    def __init__(self, name):
        self.name = name
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def find_parent(self, parent_name):
        if self.name == parent_name:
            return self
        else:
            for c in self.children:
                p = None
                if len(c.children) > 0:
                    p = c.find_parent(parent_name)
                if p != None:
                    return p
                if c.name == parent_name:
                    return c
            return None

    def print_node(self, tabs = ''):
        print(tabs + self.name if self.name else 'Parent')
        for c in self.children:
            if len(c.children) > 0:
                c.print_node(tabs + '\t')
            else:
                print(tabs + '\t' + c.name)

    #@staticmethod
    def from_path(path):
        parent = Node('')
        for root, directories, files in os.walk(path):
            name = root.replace(path, '').replace('\\', '')
            p = parent.find_parent(name)

            for directory in directories:
                p.add_child(Node(directory))

        return parent
