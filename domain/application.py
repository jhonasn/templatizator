'''Application layer module'''
from domain.model import Variable


class BaseApplication:
    '''Parent base class for application classes'''
    def __init__(self, service):
        self.service = service

    def get(self):
        '''Get model instances'''
        return self.service.get()

    def first(self, expression, collection=None):
        '''Get first model according expression
        if collection is in memory it can be passed as argument
        to avoid read from disk
        '''
        return self.service.first(expression, collection)

    def filter(self, expression, collection=None):
        '''Get models accordig expression
        if collection is in memory it can be passed as argument
        to avoid read from disk
        '''
        return self.service.filter(expression, collection)

    def add(self, model):
        '''Add model into the model collection'''
        self.service.add(model)

    def remove(self, expression):
        '''Remove model from model collection according expression'''
        self.service.remove(expression)


class NodeApplication(BaseApplication):
    '''Base class for application classes that handle node models'''
    def remove(self, node):
        '''Remove node from node collection without expression'''
        self.service.remove(node)


class FileApplication(NodeApplication):
    '''Base class for application classes that handle file models'''
    def get(self, model):
        '''Get file content according model'''
        return self.service.get(model)

    def add(self, model, content):
        '''Add file with content in the hard disk'''
        self.service.add(model, content)

    def save(self, model, new_name, content):
        '''Write file in the hard disk and rename if necessary'''
        self.service.save(model, new_name, content)

    def create_child(self, parent, name):
        '''Add child node into the parent and get correct child path'''
        return self.service.create_child(parent, name)


class ProjectApplication(BaseApplication):
    '''Exposes actions to manage configuration and project'''
    def __init__(self, service, configuration_service):
        super().__init__(service)
        self.configuration_service = configuration_service
        self.configuration_path = configuration_service.get_path()

    def get(self):
        '''Get filetree graph'''
        return self.service.get_filetree()

    def change_path(self, path):
        '''Change project path'''
        self.service.change_path(path)

    def change_configuration_path(self, path):
        '''Change configuration path'''
        self.configuration_service.change_path(path)

    @property
    def home_path(self):
        '''Get home path'''
        return self.service.get_home_path()

    def find_node(self, filetree, path):
        '''Find node instance of informed path into the filetree'''
        return self.service.find_node(filetree, path)

    def save_into_project(self):
        '''Save configured templates and configurables
        into the project folder
        '''
        self.service.save_into_project()


class VariableApplication(BaseApplication):
    '''Exposes variables basic crud actions'''
    def add(self, name, value):
        '''Add variable'''
        variable = Variable(name, value)
        self.service.add(variable)

    def change(self, old_name, name, value):
        '''Update variable'''
        variable = Variable(name, value)
        self.service.change(old_name, variable)

    def remove(self, name):
        '''Remove variable by name'''
        self.service.remove(name)


class TemplateApplication(FileApplication):
    '''Exposes template crud actions'''
    pass


class ConfigurableFileApplication(FileApplication):
    '''Exposes configurable file crud actions'''
    pass
