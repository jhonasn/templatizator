from domain.model import *

class BaseApplication:
    def __init__(self, service):
        self.service = service

class ProjectApplication(BaseApplication):
    def __init__(self, service, configuration_service):
        super().__init__(service)
        self.configuration_service = configuration_service 
        self.filetree = None

    def change_path(self, path):
        self.service.change_path(path)
        self.filetree = self.service.get_filetree()

    def change_configuration_path(self, path):
        self.configuration_service.set_path(path)

class VariablesApplication(BaseApplication):
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

class TemplateApplication(BaseApplication):
    pass

class ConfigurableFileApplication(BaseApplication):
    pass


