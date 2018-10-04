from domain.model import *

class BaseApplication:
    def __init__(self, service):
        self.service = service

    def get(self):
        return self.service.get()

    def first(self, expression, collection=None):
        return self.service.first(expression, collection)

    def filter(self, expression, collection=None):
        return self.service.filter(expression, collection)

    def add(self, model):
        self.service.add(model)

    def remove(self, expression):
        self.service.remove(expression)

class NodeApplication(BaseApplication):
    def remove(self, node):
        self.service.remove(node)

class FileApplication(NodeApplication):
    def get(self, file):
        return self.service.get(file)

    def save(self, old_name, new_name, content):
        self.service.save_file(old_name, new_name, content)

    def create_child(self, parent, name):
        return self.service.create_child(parent, name)

class ProjectApplication(BaseApplication):
    def __init__(self, service, configuration_service):
        super().__init__(service)
        self.configuration_service = configuration_service
        self.configuration_path = configuration_service.get_path()

    def get(self):
        return self.service.get_filetree()

    def change_path(self, path):
        self.service.change_path(path)

    def change_configuration_path(self, path):
        self.configuration_service.change_path(path)

    @property
    def home_path(self):
        return self.service.get_home_path()

    def find_node(self, filetree, path):
        return self.service.find_node(filetree, path)

    def save_into_project(self):
        self.service.save_into_project()

class VariableApplication(BaseApplication):
    def add(self, name, value):
        variable = Variable(name, value)
        self.service.add(variable)

    def change(self, old_name, name, value):
        variable = Variable(name, value)
        self.service.change(old_name, variable)

    def remove(self, name):
        self.service.remove(name)

class TemplateApplication(FileApplication):
    pass

class ConfigurableFileApplication(FileApplication):
    pass

