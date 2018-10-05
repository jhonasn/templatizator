from copy import copy
from domain.model import Project, Directory, Variable
from domain.infrastructure import ProjectNotSetWarning

class BaseService:
    def __init__(self, repository):
        self.repository = repository

    def get(self):
        return self.repository.get()

    def first(self, expression, collection=None):
        return self.repository.first(expression, collection)

    def filter(self, expression, collection=None):
        return self.repository.filter(expression, collection)

    def add(self, model):
        self.repository.add(model)

    def remove(self, expression):
        self.repository.remove(expression)

class NodeService(BaseService):
    def remove(self, node):
        self.repository.remove(node)

class FileService(NodeService):
    def get(self, file):
        self.repository.name = file.name
        # pylint: disable=no-value-for-parameter
        return super().get()

    def add(self, name, content):
        self.repository.name = name
        self.repository.save(content)

    def save(self, old_name, new_name, content):
        self.repository.save_file(old_name, new_name, content)

    def remove(self, model):
        self.repository.name = model.name
        self.repository.drop()

class ConfigurationService(BaseService):
    def __init__(self, service, configuration_changed_event):
        super().__init__(service)
        self.event = configuration_changed_event

    def change_path(self, path):
        self.repository.path = path
        self.event.publish(path)

    def get_path(self):
        return self.repository.path

class ProjectService(BaseService):
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
        return self.configuration_repository.get_home_path()

    def find_node(self, filetree, path):
        return self.configuration_repository.find_node(filetree, path)

    def configuration_changed(self, path):
        self.configuration_repository.path = path
        path = self.configuration_repository.get_project_path()
        if path:
            self.event.publish(path)

    def get_filetree(self):
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
                self.configuration_repository.get_parent_path(configurable.path)
            )
            if parent:
                parent.add_child(configurable)

        return filetree

    def change_path(self, path):
        project_path = self.configuration_repository.change_project(path)
        self.event.publish(project_path)

    def replace_variables(self, text):
        new_text = copy(text)
        for var in self.variable_repository.get():
            new_text = new_text.replace(f'[{var.name}]', var.value)

        return new_text

    def save_into_project(self):
        local_path = self.configuration_repository.get_project_path()
        if not local_path:
            raise ProjectNotSetWarning

        prev_name = self.template_file_repository.name
        for template in self.template_repository.get():
            self.template_file_repository.path = local_path
            self.template_file_repository.name = template.name
            content = self.template_file_repository.get()
            content = self.replace_variables(content)
            self.template_file_repository.path = self.configuration_repository.get_parent_path(template.path)
            self.template_file_repository.name = self.replace_variables(template.name)
            self.template_file_repository.save(content)

        self.template_file_repository.path = local_path
        self.template_file_repository.name = prev_name

        # TODO: implement configurable files save

class VariableService(BaseService):
    def __init__(self, repository, project_change_event):
        super().__init__(repository)
        project_change_event.subscribe(self.project_changed)

    def get_defaults(self):
        return [Variable('ext', 'py')]

    def save_defaults(self):
        if not self.repository.exists():
            for var in self.get_defaults():
                self.add(var)

    def add(self, variable):
        if not self.repository.path:
            raise ProjectNotSetWarning
        self.repository.add(variable)

    def change(self, old_name, variable):
        variables = self.get()
        v = self.repository.first(old_name, variables)
        if isinstance(v, Variable):
            v.name = variable.name
            v.value = variable.value
            self.repository.save(variables)

    def remove(self, name):
        self.repository.remove(name)

    def project_changed(self, path):
        self.repository.path = path
        self.save_defaults()

class TemplateService(FileService):
    def __init__(self, repository, template_repository, project_change_event):
        # self.repository = template_file_repository
        super().__init__(repository)
        self.template_repository = template_repository
        project_change_event.subscribe(self.project_changed)

    def project_changed(self, path):
        self.repository.path = path
        self.template_repository.path = path

    def create_child(self, parent, name):
        return self.template_repository.create_child(parent, name)

    def add(self, template, content):
        self.template_repository.add(template)
        super().add(template.name, content)

    def save(self, template, new_name, content):
        self.template_repository.update(template, new_name)
        self.repository.save_file(template.name, new_name, content)

    def remove(self, template):
        super().remove(template)
        self.template_repository.remove(template)

class ConfigurableService(FileService):
    def __init__(self, repository, configurable_repository, project_change_event):
        # self.repository = configurable_file_repository
        super().__init__(repository)
        self.configurable_repository = configurable_repository
        project_change_event.subscribe(self.project_changed)

    def project_changed(self, path):
        self.repository.path = path
        self.configurable_repository.path = path

    def create_child(self, parent, name):
        return self.configurable_repository.create_child(parent, name)

    # TODO: when implement configurable files verify if add and save methods
    # will be the same as in the template service, if yes, pass the implementation
    # to the file service wich both classes inhiret from.

