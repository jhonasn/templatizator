from copy import copy
from domain.model import Project, Directory, Variable

class BaseService:
    def __init__(self, repository):
        self.repository = repository

    def get(self):
        return self.repository.get()

    def first(self, expression, collection = None):
        return self.repository.first(expression, collection)

    def filter(self, expression, collection = None):
        return self.repository.filter(expression, collection)

    def add(self, model):
        self.repository.add(model)

    def remove(self, expression):
        self.repository.remove(expression)

# TODO: verify if will be needed, maybe this goes into the project service
class ConfigurationService(BaseService):
    def change_configuration(self, path):
        self.configuration_path = path
        self.save_history()
        self.load()

    def get_path(self):
        return self.repository.path

class ProjectService(BaseService):
    def __init__(self, configuration_repository, variable_repository,
            template_repository, configurable_repository,
            template_file_repository, configurable_file_repository,
            project_change_event):
        self.configuration_repository = configuration_repository
        self.variable_repository = variable_repository
        self.template_repository = template_repository
        self.configurable_repository = configurable_repository
        self.template_file_repository = template_file_repository
        self.configurable_file_repository = configurable_file_repository
        self.event = project_change_event

    def get(self):
        return self.configuration_repository.get_selected()

    def get_home_path(self):
        return self.configuration_repository.get_home_path()

    def find_node(self, node, path):
        if node.path == path:
            return node
        else:
            for c in node.children:
                if c.path == path:
                    return c
                elif len(c.children) > 0:
                    p = self.find_node(c, path)
                    if p != None:
                        return p
            return None

    def get_filetree(self):
        parent = self.get()
        if not parent.path:
            return parent
        iterator = self.configuration_repository.get_filetree_iter(parent.path)
        for root, directories, files in iterator:
            node = self.find_node(root, parent)

            for directory in directories:
                path = os.path.join(root, directory)
                node.add_child(Directory(path))

        templates = self.template_repository.get()
        configurables = self.configurable_repository.get()

        for t in templates:
            parent = self.find_node(self.repository.get_parent_path(t.path))
            parent.add_child(t)

        for cf in configurables:
            parent = self.service.find_node(self.repository.get_parent_path(cf.path))
            parent.add_child(cf)

        return parent

    def change_path(self, path):
        project = self.configuration_repository.change_project(path)
        self.event.publish(path)
        return project

    def replace_variables(self, text):
        new_text = copy(text)
        for v in self.variable_repository.get():
            new_text = new_text.replace(f'[{v.key}]', v.value)

        return new_text

    def save_into_project(self):
        for t in self.template_repository.get():
            self.template_file_repository.path = t.path
            self.template_file_repository.name = self.replace_variables(t.name)
            content = self.template_file_repository.get(t.path)
            content = self.replace_variables(content)
            self.template_file_repository.save(content)

        for c in self.configurable_file_repository.get():
            self.configurable_file_repository.path = c.path
            self.configurable_file_repository.name = self.replace_variables(c.name)
            content = self.configurable_file_repository.get(c.path)
            content = self.replace_variables(content)
            self.configurable_file_repository.save(content)

class VariableService(BaseService):
    def __init__(self, repository, project_change_event):
        super().__init__(repository)
        project_change_event.subscribe(self.project_changed)

    def get(self):
        variables = self.repository.get()
        if not variables or not len(variables):
            return self.get_defaults()
        else:
            return variables

    def get_defaults(self):
        return [Variable('ext', 'py')]

    def add(self, variable):
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

    def project_changed(self, name, path):
        self.repository.path = path

class TemplateService(BaseService):
    def __init__(self, repository, template_repository, project_change_event):
        # repository = template_file_repository
        super().__init__(repository)
        self.template_repository = template_repository
        project_change_event.subscribe(self.project_changed)

    def save(self, template, filename, content):
        self.save_file(template.name, filename, content)

    def project_changed(self, name, path):
        self.repository.path = path

class ConfigurableService(BaseService):
    def __init__(self, repository, configurable_repository, project_change_event):
        # repository = configurable_file_repository
        super().__init__(repository)
        self.configurable_repository = configurable_repository
        project_change_event.subscribe(self.project_changed)

    def save(self, configurable):
        self.save(configurable)

    def project_changed(self, name, path):
        self.repository.path = path
