from domain.model import *

class BaseApplication:
    def __init__(self, service):
        self.service = service

    def get(self):
        return self.service.get()

    def first(self, expression, collection = None):
        return self.service.first(expression, collection)

    def filter(self, expression, collection = None):
        return self.service.filter(expression, collection)

    def add(self, model):
        self.service.add(model)

    def remove(self, expression):
        self.service.remove(expression)

class NodeApplication(BaseApplication):
    def remove(self, node):
        self.service.remove(node)

class ProjectApplication(BaseApplication):
    def __init__(self, service, configuration_service):
        super().__init__(service)
        self.configuration_service = configuration_service 
        self.configuration_path = configuration_service.get_path()
        if self.configuration_path:
            self.filetree = self.service.get_filetree()

    def change_path(self, path):
        self.service.change_path(path)
        self.filetree = self.service.get_filetree()

    def change_configuration_path(self, path):
        self.configuration_service.set_path(path)
        self.change_path(self, path)

    @property
    def home_path(self):
        return self.service.get_home_path()

    def find_node(self, path):
        return self.service.find_node(self.filetree, path)

    def save_into_project(self):
        self.service.save_into_project()

class VariableApplication(BaseApplication):
    def __init__(self, service):
        super().__init__(service)
        self.get()

    def get(self):
        self.variables = self.service.get()

    def add(self, name, value):
        v = Variable(name, value)
        self.service.add(v)
        self.get()

    def change(self, old_name, name, value):
        v = Variable(name, value)
        self.service.change(old_name, v)
        self.get()

    def remove(self, name):
        self.service.remove(name)
        self.get()

class TemplateApplication(NodeApplication):
    pass

class ConfigurableFileApplication(NodeApplication):
    pass

