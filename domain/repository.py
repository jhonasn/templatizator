class FileRepository:
    # save files
    def __init__(self, path):
        self.path = path

    def get(self):
        return open(self.path, 'r').read()

    def save(self, content):
        open(self.path, 'w').write(content)

class JsonRepository(FileRepository):
    # save json files
    def __init__(self, path):
        super().__init__(path)

    def get(self):
        return json.loads(super().get())

    def save(self, obj):
        super().save(json.dumps(obj))

class VariableRepository(JsonRepository):
    pass

class TemplateRepository(FileRepository):
    pass

class ConfigurableFileRepository(FileRepository):
    pass

class ProjectRepository(JsonRepository):
    # save files from project, the list of
    # templates and configurable_files
    pass

class ConfigurationRepository(JsonRepository):
    # save projects in the configuration directory
    pass


