'''Application layer module'''
from abc import ABC
from templatizator.domain.domain import Variable


class ProjectApplication:
    '''Exposes actions to manage configuration and project'''
    def __init__(self, service, configuration_service):
        self.service = service
        self.configuration_service = configuration_service

    @property
    def configuration_path(self):
        return self.configuration_service.get_path()

    @property
    def home_path(self):
        '''Get home path'''
        return self.service.get_home_path()

    def get(self):
        '''Get filetree graph'''
        return self.service.get_filetree()

    def change_path(self, path):
        '''Change project path'''
        self.service.change_path(path)

    def change_configuration_path(self, path):
        '''Change configuration path'''
        self.configuration_service.change_path(path)

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


class FileApplication(ABC):
    '''Base class for file model handler classes'''
    def __init__(self, service):
        self.service = service

    def get(self, file):
        '''Get file content'''
        return self.service.get(file)

    def create_child(self, parent, name):
        '''Create child, add in the parent and return instance with attributes
        properly filled
        '''
        return self.service.create_child(parent, name)

    def add(self, file_node, content):
        '''Add file node and file'''
        self.service.add(file_node, content)

    def save(self, file_node):
        '''Save file node state'''
        self.service.save(file_node)

    def save_file(self, file_node, new_name, content):
        '''Save file node and file renaming it if necessary'''
        self.service.save_file(file_node, new_name, content)

    def remove(self, file_node):
        '''Remove file node and delete file'''
        self.service.remove(file_node)


class TemplateApplication(FileApplication):
    '''Exposes template crud actions'''
    def get_path(self, template):
        '''Get template file path'''
        return self.service.get_path(template)

    def get_all(self):
        '''Get all templates'''
        return self.service.get_all()


class ConfigurableFileApplication(FileApplication):
    '''Exposes configurable file crud actions'''
    def get_filename(self, path):
        '''Get filename from entire path'''
        return self.service.get_filename(path)

    def is_child(self, parent_path, filename):
        '''Verify if filename is a existent file into the parent_path folder'''
        return self.service.is_child(parent_path, filename)
