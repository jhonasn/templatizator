import os
import json
from copy import copy, deepcopy

from src.Node import Node

class Configuration:
    history_path = './history.json'
    # {project_path: configuration_path}
    history = {}

    def __init__(self):
        self.nodes = None
        self.project_path = None
        self.configuration_path = None

        #init history
        if os.path.exists(Configuration.history_path):
            Configuration.history = json.loads(open(Configuration.history_path).read())
        else:
            self.save_history()

        #load configuration
        if len(Configuration.history):
            self.project_path = next(iter(Configuration.history))
            self.configuration_path = Configuration.history[self.project_path]
            self.load()
        else:
            #default variables on application start
            self.__dict__['ext'] = 'py'
            
    def get_configuration_json_path(self):
        return os.path.join(self.configuration_path, 'configuration.json')

    def load(self):
        if os.path.exists(self.get_configuration_json_path()):
            configuration = json.loads(open(self.get_configuration_json_path()).read())
            # TODO: comparison beetween json nodes and project path nodes
            # self.nodes = Node.from_path(configuration['nodes']['path'])
            self.nodes = Node.from_dict(configuration['nodes']) #json_nodes
            # Node.diff(self.nodes, json_nodes)
            del configuration['nodes']
            for key, value in configuration.items():
                self.__dict__[key] = value

    def save_history(self):
        if self.project_path and self.configuration_path:
            Configuration.history[self.project_path] = self.configuration_path
        open(Configuration.history_path, 'w+').write(json.dumps(Configuration.history))

    def change_project(self, path):
        self.project_path = path
        if (self.configuration_path):
            self.save()
            self.save_history()

    def change_configuration(self, path):
        if self.configuration_path:
            os.remove(self.get_configuration_json_path())
        self.configuration_path = path
        if (self.project_path):
            self.save()
            self.save_history()

    def get_variables(self):
        cfg = deepcopy(self)
        del cfg.nodes
        del cfg.project_path
        del cfg.configuration_path
        return cfg.__dict__.items()

    def add_variable(self, name, value):
        self.__dict__[name] = value
        self.save()

    def change_variable(self, old_name, name, value):
        if old_name == name:
            self.__dict__[name] = value
        else:
            del self.__dict__[old_name]
            self.__dict__[name] = value
        self.save()

    def remove_variable(self, name):
        del self.__dict__[name]
        self.save()

    def get_template_path(self, filename):
        return os.path.join(self.configuration_path, filename)

    def get_template_content(self, node):
        return open(self.get_template_path(node.name)).read()

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

    def remove_template(self, node):
        path = self.get_template_path(node.name)
        if os.path.exists(path):
            os.remove(path)
        node.remove()
        self.save()

    def replace_variables(self, text):
        variables = self.get_variables()
        new_text = copy(text)
        for key, value in variables:
            new_text = new_text.replace(f'[{key}]', value)

        return new_text

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

    def save(self):
        if self.configuration_path:
            cfg = deepcopy(self)
            cfg.nodes = cfg.nodes.as_dict()
            open(self.get_configuration_json_path(), 'w+').write(json.dumps(cfg.__dict__))
            del cfg

configuration = Configuration()

