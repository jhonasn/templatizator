import os
import json
from domain.model import Project, Directory

class FileRepository:
    # save files
    def __init__(self, path = None):
        self.path = path

    def get_parent_path(self, path):
        return os.path.dirname(path)

    def set_path(self, path):
        self.path = path

    def exists(self, path = None):
        p = self.path if not path else os.path.join(self.path, path)
        return os.path.exists(p)

    def get(self, path = None):
        p = self.path if not path else os.path.join(self.path, path)
        return open(p, 'r').read()

    def save(self, content, path = None):
        p = self.path if not path else os.path.join(self.path, path)
        open(p, 'w').write(content)

class JsonRepository(FileRepository):
    # save json files
    def __init__(self, path = None):
        super().__init__(path)

    def get(self, path = None):
        return json.loads(super().get(path))

    def save(self, obj, path = None):
        super().save(json.dumps(obj), path)

class ConfigurationRepository(JsonRepository):
    # save projects in the configuration directory
    def __init__(self, path = None):
        if not path:
            path = os.path.join(self.default_path(), 'configuration.json')

        super().__init__(path)

    def default_path(self):
        return os.path.join(os.get_path('~'), 'templatizator')

class ProjectRepository(JsonRepository):
    # save files from project, the list of
    # templates and configurable_files
    def set_path(self, path):
        i = 0
        project_path = path
        while(os.path.exists(project_path)):
            i += 1
            project_path = path + i

        super().set_path(project_path)

    def get_filetree_iter(self, path):
        return os.walk(path)

class VariableRepository(JsonRepository):
    # save variables json
    pass

class TemplateRepository(JsonRepository):
    # save json templates
    pass

class TemplateFileRepository(FileRepository):
    # save template files
    pass

class ConfigurableRepository(JsonRepository):
    # save configurable files json
    pass

class ConfigurableFileRepository(FileRepository):
    # save configurable files
    pass
