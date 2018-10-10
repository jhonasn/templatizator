'''Application layer module'''
from domain.model import Variable


class ProjectApplication:
    '''Exposes actions to manage configuration and project'''
    def __init__(self, service, configuration_service):
        self.service = service
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


class VariableApplication:
    '''Exposes variables basic crud actions'''
    def __init__(self, service):
        self.service = service

    def get(self):
        '''Get variables'''
        return self.service.get()

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


class TemplateApplication:
    '''Exposes template crud actions'''
    def __init__(self, service):
        self.service = service

    def get(self, template):
        '''Get template file content'''
        return self.service.get(template)

    def add(self, template, content):
        '''Add template and template file'''
        self.service.add(template, content)

    def save(self, template, new_name, content):
        '''Save template and template file renaming it if necessary'''
        self.service.save(template, new_name, content)

    def remove(self, template):
        '''Remove template and delete template file'''
        self.service.remove(template)

    def create_child(self, parent, name):
        '''Create child, add in the parent and return instance with attributes
        properly filled
        '''
        return self.service.create_child(parent, name)


class ConfigurableFileApplication:
    '''Exposes configurable file crud actions'''
    def __init__(self, service):
        self.service = service
    pass
