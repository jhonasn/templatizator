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

    def get_parent_path(path):
        return os.path.dirname(path)

    def get_parent_path(self, path):
        return FileRepository.get_parent_path(self.path)

    @property
    def full_path(self):
        if self.path and self.name:
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

    # get untyped
    def get_json(self):
        if self.exists():
            return json.loads(super().get())
        else:
            return None

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
                for i in result:
                    v = deserialization_type()
                    v.__dict__ = i
                    value.append(v)

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

class ConfigurationRepository(JsonRepository):
    # save projects in the configuration directory
    name = 'configuration.json'
    of_type = Project

    def __init__(self, path = None):
        if not path:
            path = self.default_path()

        super().__init__(path)

    def default_path(self):
        return os.path.join(self.get_home_path(), 'templatizator')

    def get_home_path(self):
        return os.path.expanduser('~')

    def change_project(self, path):
        i = 0
        project = self.first(lambda p: p.path == path)
        if not project:
            # set friendly project name
            name = os.path.basename(path)
            localpath = os.path.join(self.path, name)
            while(os.path.exists(localpath)):
                i += 1
                name += f'-{i}'
                localpath = os.path.join(self.path, name)
            project = Project(path, name, True)
            projects = self.get()
            for p in projects:
                p.selected = False
            projects.append(project)
            self.save(projects)
        return project

    def get_filetree_iter(self, path):
        return os.walk(path)

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

class TemplateRepository(JsonRepository):
    # save json templates
    name = 'templates.json'
    of_type = Template

class TemplateFileRepository(FileRepository):
    # save template files
    pass

class ConfigurableRepository(JsonRepository):
    # save configurable files json
    name = 'configurablefiles.json'
    of_type = ConfigurableFile

class ConfigurableFileRepository(FileRepository):
    # save configurable files
    pass

