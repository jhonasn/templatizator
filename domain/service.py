'''Service layer module'''
from copy import copy
from domain.model import Variable
from domain.infrastructure import ProjectNotSetWarning


class BaseService:
    '''Parent base class for service classes'''
    def __init__(self, repository):
        self.repository = repository

    def get(self):
        '''Get model instances'''
        return self.repository.get()

    def first(self, expression, collection=None):
        '''Get first model according expression
        if collection is in memory it can be passed as argument
        to avoid read from disk
        '''
        return self.repository.first(expression, collection)

    def filter(self, expression, collection=None):
        '''Get models accordig expression
        if collection is in memory it can be passed as argument
        to avoid read from disk
        '''
        return self.repository.filter(expression, collection)

    def add(self, model):
        '''Add model into the model collection'''
        self.repository.add(model)

    def remove(self, expression):
        '''Remove model from model collection according expression'''
        self.repository.remove(expression)


class NodeService(BaseService):
    '''Base class for service classes that handle node models'''
    def remove(self, node):
        '''Remove node from node collection without expression'''
        self.repository.remove(node)


class FileService(NodeService):
    '''Base class for service classes that handle file models'''
    def get(self, file):
        '''Get file content according model'''
        self.repository.name = file.name
        # pylint: disable=no-value-for-parameter
        return super().get()

    def add(self, name, content):
        '''Add file with content in the hard disk'''
        self.repository.name = name
        self.repository.save(content)

    def save(self, old_name, new_name, content):
        '''Write file in the hard disk and rename if necessary'''
        self.repository.save_file(old_name, new_name, content)

    def remove(self, model):
        '''Deletes file from hard disk according to node model'''
        self.repository.name = model.name
        self.repository.drop()


class ConfigurationService(BaseService):
    '''Handle configuration rules'''
    def __init__(self, service, configuration_changed_event):
        super().__init__(service)
        self.event = configuration_changed_event

    def change_path(self, path):
        '''Changes repository path and notify it through event'''
        self.repository.path = path
        self.event.publish(path)

    def get_path(self):
        '''Returns configuration path'''
        return self.repository.path


class ProjectService(BaseService):
    '''Handle project rules'''
    # Project has no repository so its not necessary to call base class
    # pylint: disable=super-init-not-called,too-many-arguments
    def __init__(self, configuration_repository, variable_repository,
                 template_repository, configurable_repository,
                 template_file_repository, configurable_file_repository,
                 configuration_changed_event, project_change_event):
        self.configuration_repository = configuration_repository
        self.variable_repository = variable_repository
        self.template_repository = template_repository
        self.configurable_repository = configurable_repository
        self.template_file_repository = template_file_repository
        self.configurable_file_repository = configurable_file_repository
        self.event = project_change_event

        configuration_changed_event.subscribe(self.configuration_changed)

        path = self.configuration_repository.get_project_path()
        if path:
            self.event.publish(path)

    def get_home_path(self):
        '''Get home path'''
        return self.configuration_repository.get_home_path()

    def find_node(self, filetree, path):
        '''Find node instance of informed path into the filetree'''
        return self.configuration_repository.find_node(filetree, path)

    def configuration_changed(self, path):
        '''Configuration path change listener, change path when receives a
        notification from configuration and notify other services through event
        '''
        self.configuration_repository.path = path
        path = self.configuration_repository.get_project_path()
        if path:
            self.event.publish(path)

    def get_filetree(self):
        '''Get filetree graph and fills it with templates and configurables'''
        filetree = self.configuration_repository.get_filetree()

        templates = self.template_repository.get()
        configurables = self.configurable_repository.get()

        for template in templates:
            parent = self.find_node(
                filetree,
                self.configuration_repository.get_parent_path(template.path)
            )
            if parent:
                parent.add_child(template)

        for configurable in configurables:
            parent = self.find_node(
                filetree,
                self.configuration_repository.get_parent_path(
                    configurable.path
                )
            )
            if parent:
                parent.add_child(configurable)

        return filetree

    def change_path(self, path):
        '''Changes repository path and notify it through event'''
        project_path = self.configuration_repository.change_project(path)
        self.event.publish(project_path)

    def replace_variables(self, text):
        '''Replaces placeholders in the passed text with
        recorded application variables
        '''
        new_text = copy(text)
        for var in self.variable_repository.get():
            new_text = new_text.replace(f'[{var.name}]', var.value)

        return new_text

    def save_into_project(self):
        '''Save configured templates and configurables
        into the project folder
        '''
        local_path = self.configuration_repository.get_project_path()
        if not local_path:
            raise ProjectNotSetWarning

        prev_name = self.template_file_repository.name
        for template in self.template_repository.get():
            self.template_file_repository.path = local_path
            self.template_file_repository.name = template.name
            content = self.template_file_repository.get()
            content = self.replace_variables(content)
            self.template_file_repository.path = \
                self.configuration_repository.get_parent_path(template.path)
            self.template_file_repository.name = \
                self.replace_variables(template.name)
            self.template_file_repository.save(content)

        self.template_file_repository.path = local_path
        self.template_file_repository.name = prev_name

        # TODO: implement configurable files save


class VariableService(BaseService):
    '''Handle variable rules'''
    def __init__(self, repository, project_change_event):
        super().__init__(repository)
        project_change_event.subscribe(self.project_changed)

    @staticmethod
    def get_defaults():
        '''Returns default application variables'''
        return [Variable('ext', 'py')]

    def save_defaults(self):
        '''Saves default variables if them aren\'t deleted before'''
        if not self.repository.exists():
            for var in VariableService.get_defaults():
                self.add(var)

    def add(self, variable):
        '''Add variable'''
        if not self.repository.path:
            raise ProjectNotSetWarning
        self.repository.add(variable)

    def change(self, old_name, variable):
        '''Updates variable'''
        variables = self.get()
        db_variable = self.repository.first(old_name, variables)
        if isinstance(db_variable, Variable):
            db_variable.name = variable.name
            db_variable.value = variable.value
            self.repository.save(variables)

    def remove(self, name):
        '''Removes variable by name'''
        self.repository.remove(name)

    def project_changed(self, path):
        '''Project path change listener that change repository path when
        project path is changed
        '''
        self.repository.path = path
        self.save_defaults()


class TemplateService(FileService):
    '''Handle template rules'''
    def __init__(self, repository, template_repository, project_change_event):
        # self.repository = template_file_repository
        super().__init__(repository)
        self.template_repository = template_repository
        project_change_event.subscribe(self.project_changed)

    def project_changed(self, path):
        '''Project path change listener that change repository path when
        project path is changed
        '''
        self.repository.path = path
        self.template_repository.path = path

    def create_child(self, parent, name):
        '''Add child node into the parent and get correct child path'''
        return self.template_repository.create_child(parent, name)

    def add(self, template, content):
        '''Add file with content in the hard disk'''
        self.template_repository.add(template)
        super().add(template.name, content)

    def save(self, template, new_name, content):
        '''Write file in the hard disk and rename if necessary'''
        self.template_repository.update(template, new_name)
        self.repository.save_file(template.name, new_name, content)

    def remove(self, template):
        '''Removes template from collection and its file'''
        super().remove(template)
        self.template_repository.remove(template)


class ConfigurableService(FileService):
    '''Handle configurable rules'''
    def __init__(self, repository, configurable_repository,
                 project_change_event):
        # self.repository = configurable_file_repository
        super().__init__(repository)
        self.configurable_repository = configurable_repository
        project_change_event.subscribe(self.project_changed)

    def project_changed(self, path):
        '''Project path change listener that change repository path when
        project path is changed
        '''
        self.repository.path = path
        self.configurable_repository.path = path

    def create_child(self, parent, name):
        '''Add child node into the parent and get correct child path'''
        return self.configurable_repository.create_child(parent, name)

    # TODO: when implement configurable files verify if add and save methods
    # will be the same as in the template service, if yes, pass
    # the implementation to the file service wich both classes inhiret from.
