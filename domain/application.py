class BaseApplication:
    def __init__(self, service):
        self.service = service

class ProjectApplication(BaseApplication):
    def __init__(self, service, configuration_service):
        super().__init__(service)
        self.configuration_service = configuration_service 
        self.filetree = None

    def change_path(self, path):
        self.service.change_path(path)
        self.filetree = self.service.get_filetree(path)

    def change_configuration_path(self, path):
        self.configuration_service.set_path(path)

class VariablesApplication(BaseApplication):
    pass

class TemplateApplication(BaseApplication):
    pass

class ConfigurableFileApplication(BaseApplication):
    pass

class Configuration:
    def __init__(self):
        self.nodes = None
        self.project_path = None
        self.configuration_path = None

        #load configuration
        if len(Configuration.history):
            self.configuration_path = Configuration.history[-1]
            self.load()
        else:
            self.set_default_variables()

    def load(self):
        path = self.get_configuration_json_path()
        will_load = os.path.exists(path)

        self.clear_variables()
        self.set_default_variables()
        self.project_path = None
        self.nodes = None

        if will_load:
            configuration = json.loads(open(path).read())

            # TODO: comparison beetween json nodes and project path nodes
            # self.nodes = Node.from_path(configuration['nodes']['path'])
            self.nodes = Node.from_dict(configuration['nodes']) #json_nodes
            # Node.diff(self.nodes, json_nodes)
            del configuration['nodes']
            for key, value in configuration.items():
                # project_path is loaded (or not) here too
                self.__dict__[key] = value

        return will_load

    def save_history(self):
        if self.configuration_path and self.configuration_path not in Configuration.history:
            Configuration.history.append(self.configuration_path)
        elif self.configuration_path:
            # The configuration already exists in history and it was selected again
            # so we append it in de history to be the most recent configuration
            Configuration.history.remove(self.configuration_path)
            Configuration.history.append(self.configuration_path)
        open(Configuration.history_path, 'w+').write(json.dumps(Configuration.history))

    def change_configuration(self, path):
        self.configuration_path = path
        self.save_history()
        self.load()

    def clear_variables(self):
        variables = self.get_variables()
        for key in list(variables):
            del self.__dict__[key]

    def get_variables(self):
        cfg = deepcopy(self)
        del cfg.nodes
        del cfg.project_path
        del cfg.configuration_path
        return cfg.__dict__

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
        for key, value in variables.items():
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

