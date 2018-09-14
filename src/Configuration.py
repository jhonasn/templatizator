import os
import json
from copy import deepcopy

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

    def get_configuration_json_path(self):
        return os.path.join(self.configuration_path, 'configuration.json')

    def load(self):
        if os.path.exists(self.get_configuration_json_path()):
            configuration = json.loads(open(self.get_configuration_json_path()))
            for key, value in configuration:
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
            os.path.remove(self.configuration_path)
        self.configuration_path = path
        if (self.project_path):
            self.save()
            self.save_history()

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

    def save_template(self, node, filename, content):
        if node.name != filename:
            old_path = node.path
            self.path = os.path.join(node.path, filename)
            self.name = filename

            if os.path.exists(old_path):
                os.rename(old_path, self.path)

        if self.configuration_path:
            open(os.path.join(self.configuration_path, node.name), 'w+').write(content)

        self.save()

    def save(self):
        if self.configuration_path:
            cfg = deepcopy(self)
            cfg.nodes = cfg.nodes.as_dict()
            open(self.get_configuration_json_path(), 'w+').write(json.dumps(cfg.__dict__))
            del cfg
