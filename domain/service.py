from domain.model import Project, Directory, Variable

class BaseService:
    def __init__(self, repository):
        self.repository = repository

class ProjectService(BaseService):
    def __init__(self, repository, template_repository, configurable_repository):
        super().__init__(repository)
        self.template_repository = template_repository
        self.configurable_repository = configurable_repository

    def find_node(self, node, path):
        if node.path == path:
            return node
        else:
            for c in node.children:
                if c.path == path:
                    return c
                elif len(c.children) > 0:
                    p = self.find_node(c, path)
                    if p != None:
                        return p
            return None

    def get_filetree(self, path):
        parent = Project(path)
        for root, directories, files in self.repository.get_filetree_iter(path):
            node = self.find_node(root, parent)

            for directory in directories:
                path = os.path.join(root, directory)
                node.add_child(Directory(path))

        templates = self.template_repository.get()
        configurables = self.configurable_repository.get()

        for t in templates:
            parent = self.find_node(self.repository.get_parent_path(t.path))
            parent.add_child(t)

        for cf in configurables:
            parent = self.service.find_node(self.repository.get_parent_path(cf.path))
            parent.add_child(cf)

        return parent

    def change_path(self, path):
        self.repository.set_path(path)

class VariablesService(BaseService):
    def __init__(self, repository):
        self.variables = []
        self.load()

    def load(self):
        if self.repository.exists():
            self.variables = self.repository.get()
        else:
            self.set_defaults()

    def set_defaults(self):
        self.variables.append(Variable('ext', 'py'))

class ConfigurationService(BaseService):
    pass

class TemplateService(BaseService):
    pass

class ConfigurableFileService(BaseService):
    pass

'''
class Node:
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
'''

