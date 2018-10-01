class BaseService:
    def __init__(self, repository):
        self.repository = repository

class ProjectService(BaseService):
    pass

class ConfigurationService(BaseService):
    pass

class TemplateService(BaseService):
    pass

class ConfigurableFileService(BaseService):
    pass

'''
class Node:
    def create_child(self, name):
        child = Node(os.path.join(self.path, name))
        self.add_child(child)
        return child

    def find(self, path):
        if self.path == path:
            return self
        else:
            for c in self.children:
                if c.path == path:
                    return c
                elif len(c.children) > 0:
                    p = c.find(path)
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

    def from_dict(node_dict):
        parent = Node(node_dict['path'])
        parent.__dict__ = node_dict.copy()
        if not hasattr(parent, 'parent'):
            parent.parent = None
        parent.children = []
        for c in node_dict['children']:
            if len(c['children']):
                c['parent'] = parent
                parent.children.append(Node.from_dict(c))
            else:
                cn = Node(c['path'])
                cn.__dict__ = c.copy()
                cn.children = []
                cn.parent = parent
                parent.children.append(cn)

        return parent

    def as_dict(self):
        parent = copy(self)
        del parent.parent

        for c in parent.children:
            i = parent.children.index(c)
            if len(c.children):
                parent.children[i] = c.as_dict()
            else:
                cc = copy(c)
                del cc.parent
                parent.children[i] = cc.__dict__

        return parent.__dict__

    def get_file_nodes(self, files = []):
        if not self.is_directory:
            files.append(self)

        for c in self.children:
            if len(c.children):
                c.get_file_nodes(files)
            elif not c.is_directory:
                files.append(c)
        
        return files

    def print_node(self, tabs = ''):
        print(tabs + self.name if self.name else 'Parent')
        for c in self.children:
            if len(c.children):
                c.print_node(tabs + '\t')
            else:
                print(tabs + '\t' + c.name)

    def fill_treeview(self, treeview, parent_id = ''):
        if not parent_id:
            parent_id = treeview.insert(
                parent_id, 'end', self.path, text=self.get_name(),
                values=self.get_actions(), open=True)

        for c in self.children:
            child_parent_id = treeview.insert(
                parent_id, 'end', c.path, text=c.get_name(),
                values=c.get_actions(), open=c.open)
            if len(c.children):
                c.fill_treeview(treeview, child_parent_id)
'''

