'''Service layer module'''
from abc import ABC
from domain.model import Variable
from domain.infrastructure import ProjectNotSetWarning


class ConfigurationService:
    '''Handle configuration rules'''
    def __init__(self, repository, configuration_changed_event):
        self.repository = repository
        self.event = configuration_changed_event

    def change_path(self, path):
        '''Changes repository path and notify it through event'''
        self.repository.path = path
        self.event.publish(path)

    def get_path(self):
        '''Returns configuration path'''
        return self.repository.path


class ProjectService:
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
        new_text = text
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
            if template.save:
                self.template_file_repository.path = local_path
                self.template_file_repository.name = template.name
                content = self.template_file_repository.get()
                content = self.replace_variables(content)
                self.template_file_repository.path = \
                    self.configuration_repository.get_parent_path(
                        template.path)
                self.template_file_repository.name = \
                    self.replace_variables(template.name)
                self.template_file_repository.save(content)

        self.template_file_repository.path = local_path
        self.template_file_repository.name = prev_name

        # TODO: implement configurable files save here too


class VariableService:
    '''Handle variable rules'''
    def __init__(self, repository, project_change_event):
        self.repository = repository
        project_change_event.subscribe(self.project_changed)

    def get(self):
        '''Get project variables'''
        return self.repository.get()

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
        variables = self.repository.get()
        db_variable = self.repository.first(lambda v: v.name == old_name,
                                            variables)
        if isinstance(db_variable, Variable):
            db_variable.name = variable.name
            db_variable.value = variable.value
            self.repository.save(variables)

    def remove(self, name):
        '''Removes variable by name'''
        self.repository.remove(lambda v: v.name == name)

    def project_changed(self, path):
        '''Project path change listener that change repository path when
        project path is changed
        '''
        self.repository.path = path
        self.save_defaults()


class FileService(ABC):
    '''Base service class for file model handlers'''
    def __init__(self, repository, file_repository):
        self.repository = repository
        self.file_repository = file_repository

    def create_child(self, parent, name):
        '''Add child node into the parent and get correct child path'''
        return self.repository.create_child(parent, name)


class TemplateService(FileService):
    '''Handle template rules'''
    def __init__(self, repository, file_repository, project_change_event):
        super().__init__(repository, file_repository)
        project_change_event.subscribe(self.project_changed)

    def get(self, template):
        '''Get file content'''
        self.file_repository.name = template.name
        return self.file_repository.get()

    def project_changed(self, path):
        '''Project path change listener that change repository path when
        project path is changed
        '''
        self.file_repository.path = path
        self.repository.path = path

    def get_path(self, template):
        '''Get template file path'''
        self.repository.name = template.name
        return self.repository.full_path

    def add(self, template, content):
        '''Add file with content in the hard disk'''
        self.repository.add(template)
        self.file_repository.name = template.name
        self.file_repository.save(content)

    def save(self, template):
        '''Save template state'''
        self.repository.update(template, template.name)

    def save_file(self, template, new_name, content):
        '''Write file in the hard disk and rename if necessary'''
        self.repository.update(template, new_name)
        self.file_repository.save_file(template.name, new_name, content)

    def remove(self, template):
        '''Removes template from collection and its file'''
        self.repository.remove_node(template)
        self.file_repository.name = template.name
        self.file_repository.drop()


class ConfigurableService(FileService):
    '''Handle configurable rules'''
    def __init__(self, repository, file_repository, project_change_event):
        super().__init__(repository, file_repository)
        project_change_event.subscribe(self.project_changed)

    def get(self, configurable):
        '''Get file content'''
        self.file_repository.full_path = configurable.path
        return self.file_repository.get()

    def project_changed(self, path):
        '''Project path change listener that change repository path when
        project path is changed
        '''
        self.repository.path = path
        self.file_repository.path = path

    def get_filename(self, path):
        '''Get filename from entire path'''
        return self.repository.get_basename(path)

    def is_child(self, parent_path, filename):
        '''Verify if filename is a existent file into the parent_path folder'''
        return self.repository.is_child(parent_path, filename)
