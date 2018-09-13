import os

class Node:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.children = []

    def add_child(self, child):
        self.children.append(child)

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

    def print_node(self, tabs = ''):
        print(tabs + self.name if self.name else 'Parent')
        for c in self.children:
            if len(c.children) > 0:
                c.print_node(tabs + '\t')
            else:
                print(tabs + '\t' + c.name)
'''
    def fill_treeview(self, treeview, is_parent = True):
        if is_parent
            parent_row = treeview.append(self.name)

        for c in self.children:
            parent_row.append(c.name) 
            if len(c.children) > 0:
                c.fill_treeview(treeview, False)
'''

