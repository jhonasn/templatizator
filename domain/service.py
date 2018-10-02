from copy import copy
from domain.model import Project, Directory, Variable

class BaseService:
    def __init__(self, repository):
        self.repository = repository

    def get(self):
        return self.repository.get()

    def first(self, expression, collection = None):
        return self.repository.first(expression, collection)

    def find(self, expression, collection = None):
        return self.repository.find(expression, collection)

    def add(self, model):
        self.repository.add(model)

    def remove(self, expression):
        self.repository.remove(expression)

class ConfigurationService(BaseService):
    def change_configuration(self, path):
        self.configuration_path = path
        self.save_history()
        self.load()

class ProjectService(BaseService):
    def __init__(self, repository, template_repository, configurable_repository, project_change_event):
        super().__init__(repository)
        self.template_repository = template_repository
        self.configurable_repository = configurable_repository
        self.event = project_change_event

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
        parent = Project(self.repository.path)
        for root, directories, files in self.repository.get_filetree_iter(path):
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
        self.repository.path = path
        self.event.publish(path)

    '''
    def save_templates_into_project(self):
        templates = self.nodes.get_file_nodes()

        for t in templates:
            path = os.path.dirname(t.path)
            path = os.path.join(path, self.replace_variables(t.name))
            open(path, 'w+').write(
                self.replace_variables(
                    self.get_template_content(t)
                )
            )
    '''

class VariableService(BaseService):
    def __init__(self, repository, project_change_event):
        self.load()
        project_change_event.subscribe(self.project_changed)

    def get(self):
        variables = self.repository.get()
        if not self.variables or not len(self.variables):
            return get_defaults()
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

    def replace_variables(self, text):
        new_text = copy(text)
        for v in self.get():
            new_text = new_text.replace(f'[{v.key}]', v.value)

        return new_text

    def project_changed(name, path):
        self.repository.path = path
        self.variables.clear()
        self.load()

class TemplateFileService(BaseService):
    '''
    def save_template(self, node, filename, content):
        old_name = node.name
        dir_path = os.path.dirname(node.path)
        node.path = os.path.join(dir_path, filename)
        node.name = filename

        if self.configuration_path:
            old_path = self.get_template_path(old_name)
            new_path = self.get_template_path(filename)

            if os.path.exists(old_path):
                os.rename(old_path, new_path)

            open(new_path, 'w+').write(content)

        self.save()
    '''
    pass

class ConfigurableFileService(BaseService):
    pass

