import os
import json
from domain.model import *
from abc import ABC

class FileRepository(ABC):
    # save files

    name = None

    def __init__(self, path = None, name = None):
        self.path = path
        if type(self).name:
            self.name = type(self).name
        self.name = name

    def get_parent_path(self, path):
        return os.path.dirname(path)

    def get_basename(self, path):
        return os.path.basename(path)

    @property
    def full_path(self):
        name = self.name if hasattr(self, 'name') and self.name else type(self).name
        if self.path and name:
            return os.path.join(self.path, self.name)
        else:
            return None

    def exists(self):
        if not self.full_path: return False
        return os.path.exists(self.full_path)

    def get(self):
        if self.exists():
            return open(self.full_path, 'r').read()
        else:
            return ''

    def save(self, content):
        if self.full_path:
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            open(self.full_path, 'w').write(content)

    def drop(self):
        if self.full_path:
            os.remove(self.full_path)

    def save_file(self, old_name, new_name, content):
        if old_name != new_name:
            self.name = old_name
            self.drop()

        self.name = new_name
        self.save(content)

class JsonRepository(FileRepository):
    # save object list as json

    # deserialization type
    of_type = None

    def __init__(self, path = None):
        super().__init__(path)
        del self.name

    # get untyped
    def get_json(self):
        if self.exists():
            return json.loads(super().get())
        else:
            return []

    def save(self, collection):
        super().save(json.dumps(
                list(map(
                    lambda i: i.serialize() if isinstance(i, Serializable) else i.__dict__,
                    collection
                ))
        ))

    def get(self):
        result = self.get_json()
        value = []
        deserialization_type = type(self).of_type

        if result:
            if not deserialization_type:
                value = result
            else:
                for item in result:
                    # pylint: disable=not-callable
                    value_item = deserialization_type()
                    for key, val in item.items():
                        value_item.__dict__[key] = val
                    value.append(value_item)

        return value

    def first(self, expression, collection = None):
        if not collection:
            collection = self.get()
        results = self.filter(expression, collection)
        return results[0] if len(results) else None

    def filter(self, expression, collection = None):
        if not collection:
            collection = self.get()
        if not collection:
            collection = []
        return list(filter(expression, collection))

    def add(self, model):
        collection = self.get()

        if not collection or len(collection):
            collection = []

        collection.append(model)
        self.save(collection)

    def remove(self, expression):
        collection = self.get()
        m = self.first(expression)
        if m:
            collection.remove(m)
        self.save(collection)

class NodeRepository(JsonRepository):
    def get(self):
        nodes = super().get()
        for node in nodes:
            node.name = self.get_basename(node.path)

        return nodes

    def remove(self, node):
        super().remove(lambda n: n.path == node.path)

    def create_child(self, parent, name):
        # pylint: disable=not-callable
        child = type(self).of_type(os.path.join(parent.path, name), name)
        parent.add_child(child)
        return child

class ConfigurationRepository(JsonRepository):
    # save projects in the configuration directory
    name = 'configuration.json'
    of_type = Project

    def __init__(self, path = None):
        if not path:
            path = self.default_path()

        super().__init__(path)

    def get(self):
        projects = super().get()
        for p in projects:
            p.name = self.get_basename(p.path)

        return projects

    def default_path(self):
        return os.path.join(self.get_home_path(), 'templatizator')

    def get_home_path(self):
        return os.path.expanduser('~')

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

    def get_filetree(self):
        parent = self.get_selected()
        if not parent.path:
            return parent
        parent.name = self.get_basename(parent.path)

        for root, directories, files in os.walk(parent.path):
            node = self.find_node(parent, root)

            for directory in directories:
                path = os.path.join(root, directory)
                node.add_child(Directory(path, directory))

        return parent

    def change_project(self, path):
        projects = self.get()
        project = self.first(lambda p: p.path == path, projects)

        # unselect projects
        for p in projects:
            p.selected = False

        if not project:
            # add new project

            # set friendly project name
            path_name = self.get_basename(path)
            name = path_name
            i = 0
            while(self.first(lambda p: p.name == path_name)):
                i += 1
                path_name = f'{name}-{i}'
            project = Project(path, name, path_name, True)
            projects.append(project)
        else:
            # project already exist, select project
            project.selected = True

        self.save(projects)

        return project

    def get_filetree_iter(self, path):
        return

    def get_selected(self):
        selected = self.first(lambda p: p.selected)
        return selected if selected else Project()

class VariableRepository(JsonRepository):
    # save variables json
    name = 'variables.json'
    of_type = Variable

    def first(self, name, variables):
        return super().first(lambda v: v.name == name, variables)

    def remove(self, name):
        super().remove(lambda v: v.name == name)

class TemplateRepository(NodeRepository):
    # save json templates
    name = 'templates.json'
    of_type = Template

class TemplateFileRepository(FileRepository):
    # save template files
    pass

class ConfigurableRepository(NodeRepository):
    # save configurable files json
    name = 'configurablefiles.json'
    of_type = ConfigurableFile

class ConfigurableFileRepository(FileRepository):
    # save configurable files
    pass

