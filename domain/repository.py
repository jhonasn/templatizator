import os
import json
from domain.model import *

class FileRepository:
    # save files

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
        else
            return None

    def exists(self):
        return os.path.exists(self.full_path)

    def get(self):
        if self.exists():
            return open(self.full_path, 'r').read()
        else:
            return ''

    def save(self, content):
        open(self.full_path, 'w').write(content)

class JsonRepository(FileRepository):
    # save json files

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

    def save(self, obj):
        super().save(json.dumps(obj))

    def get(self):
        result = self.get_json()
        value = None
        deserialization_type = type(self).of_type

        if not deserialization_type:
            value = result
        elif isinstance(result, list):
            value = []
            for i in result:
                v = deserialization_type()
                v.__dict__ = i
        else:
            value = deserialization_type()
            value.__dict__ = result

        return value

    def first(self, expression, collection = None):
        if not collection
            collection = self.get()
        iterable = find(expression, collection)
        return next(iterable)

    def find(self, expression, collection = None):
        if not collection
            collection = self.get()
        return find(expression, collection)

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

    def __init__(self, path = None, name = None):
        if not path:
            path = self.default_path()

        super().__init__(path, name)

    def default_path(self):
        return os.path.join(os.get_path('~'), 'templatizator')

    def set_project_path(self, path):
        i = 0
        project_path = path
        while(os.path.exists(project_path)):
            i += 1
            project_path = path + i

        super().set_path(project_path)

    def get_filetree_iter(self, path):
        return os.walk(path)

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

