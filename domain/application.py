from domain.model import *

class BaseApplication:
    def __init__(self, service):
        self.service = service

class ProjectApplication(BaseApplication):
    def __init__(self, service, configuration_service):
        super().__init__(service)
        self.configuration_service = configuration_service 
        self.project = None
        self.filetree = None
        self.configuration_path = configuration_service.get_path()
        if self.configuration_path:
            self.project = self.service.get()
            self.filetree = self.service.get_filetree()

    def change_path(self, path):
        self.project = self.service.change_path(path)
        self.filetree = self.service.get_filetree()

    def change_configuration_path(self, path):
        self.configuration_service.set_path(path)
        self.change_path(self, path)

    @property
    def home_path(self):
        return self.service.get_home_path()

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

class TemplateApplication(BaseApplication):
    pass

class ConfigurableFileApplication(BaseApplication):
    pass

