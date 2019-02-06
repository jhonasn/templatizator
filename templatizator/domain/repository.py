'''Repository layer module'''
import os
import json
from abc import ABC
from templatizator.domain.infrastructure import RepositoryPathNotSet
from templatizator.domain.domain import Serializable, Project, Directory, \
    Template, ConfigurableFile, Variable


class FileRepository(ABC):
    '''CRUD files from hard drive and handle os interactions
    The full path of repository is mouted with path and name expecting that the
    name is a name of file. The name can either passed in name static attribute
    or as constructor argument
    '''
    # save files

    name = None

    def __init__(self, path=None, name=None):
        self.path = path
        if type(self).name:
            self.name = type(self).name
        self.name = name

    @classmethod
    def get_parent_path(cls, path):
        '''Returns parent folder from path passed'''
        return os.path.dirname(path)

    @classmethod
    def get_basename(cls, path):
        '''Returns the name of file or folder path passed'''
        return os.path.basename(path)

    @property
    def full_path(self):
        '''Mount and returns full path of repository'''
        name = self.name \
            if hasattr(self, 'name') and self.name \
            else type(self).name
        if self.path and name:
            return os.path.join(self.path, self.name)
        elif self.path:
            return self.path

        return None

    @full_path.setter
    def full_path(self, path):
        self.name = self.get_basename(path)
        self.path = self.get_parent_path(path)

    def exists(self):
        '''Returns True if the repository full_path already exists'''
        if not self.full_path:
            return False
        return os.path.exists(self.full_path)

    def get(self):
        '''Returns the content of file hadled by the repository'''
        if self.exists():
            with open(self.full_path, 'r') as f:
                return f.read()

        return ''

    def save(self, content):
        '''Write the content into the file pointed by the full_path of repo'''
        if self.full_path:
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            with open(self.full_path, 'w') as f:
                f.write(content)
        else:
            raise RepositoryPathNotSet(type(self).__name__)

    def drop(self):
        '''Deletes the repository file'''
        if self.full_path and os.path.exists(self.full_path):
            os.remove(self.full_path)

    def save_file(self, old_name, new_name, content):
        '''Write the repository file if the name is the same, else
        delete the old repository file and save the new repo. file
        '''
        if old_name != new_name:
            self.name = old_name
            self.drop()

        self.name = new_name
        self.save(content)


class JsonRepository(FileRepository):
    '''Handle collections saving as json into the hard drive.
    The 'of_type' static attribute expects to be the model type of collection
    that the repository handle. If this attribute is informed the repository
    will convert the objects of json to this type, else it will return a dict
    object with the contents of json.
    '''
    # save object list as json

    # deserialization type
    of_type = None

    def __init__(self, path=None):
        super().__init__(path)
        del self.name

    # get untyped
    def get_json(self):
        '''Returns a collection of dict objects withou trying to convert'''
        if self.exists():
            return json.loads(super().get())

        return []

    # Overriding save file with object is necessary to the purpouse of saving
    # a json file
    # pylint: disable=arguments-differ
    def save(self, collection):
        '''Save the collection passed as json'''
        collection_serialized = list(map(
            lambda i: (
                i.serialize()
                if isinstance(i, Serializable)
                else i.__dict__
            ),
            collection
        ))
        super().save(json.dumps(collection_serialized))

    def get(self):
        '''Returns a collection of objects trying to
        convert to informed of_type attribute
        '''
        json_result = self.get_json()
        result = []
        deserialization_type = type(self).of_type

        if json_result:
            if not deserialization_type:
                result = json_result
            else:
                for json_item in json_result:
                    # pylint: disable=not-callable
                    item = deserialization_type()
                    for key in json_item.keys():
                        item.__dict__[key] = json_item[key]
                    result.append(item)

        return result

    def first(self, expression, collection=None):
        '''Get first model according expression
        if collection is in memory it can be passed as argument
        to avoid read from disk
        '''
        if not collection:
            collection = self.get()
        results = self.filter(expression, collection)
        return results[0] if results else None

    def filter(self, expression, collection=None):
        '''Get models accordig expression
        if collection is in memory it can be passed as argument
        to avoid read from disk
        '''
        if not collection:
            collection = self.get()
        if not collection:
            collection = []
        return list(filter(expression, collection))

    def add(self, model):
        '''Add model into the model collection'''
        collection = self.get()
        collection.append(model)
        self.save(collection)

    def remove(self, expression):
        '''Remove model from domain collection according expression'''
        collection = self.get()
        model = self.first(expression, collection)
        if model:
            collection.remove(model)
        self.save(collection)


class NodeRepository(JsonRepository):
    '''Base repository class to handle models that are nodes'''
    def get(self):
        '''Returns a collection of nodes setting the name'''
        nodes = super().get()
        for node in nodes:
            node.name = self.get_basename(node.path)

        return nodes

    def add(self, model):
        '''Add a node into the node collection'''
        self.update_path(model)
        super().add(model)

    def update(self, node, new_name):
        '''Update the node taking care to rename path and name it correctly'''
        nodes = self.get()
        db_node = self.first(lambda n: n.path == node.path, nodes)
        db_node.name = new_name
        self.update_path(db_node)
        db_node.save = node.save
        super().save(nodes)
        node.name = db_node.name
        node.path = db_node.path

    def remove_node(self, node):
        '''Remove node by path'''
        super().remove(lambda n: n.path == node.path)

    def create_child(self, parent, name):
        '''Add child node into the parent and get correct child path'''
        # pylint: disable=not-callable
        child = type(self).of_type(os.path.join(parent.path, name), name)
        parent.add_child(child)
        return child

    def update_path(self, node):
        '''Update node path corretly according path and name'''
        node.path = self.get_parent_path(node.path)
        node.path = os.path.join(node.path, node.name)


class ConfigurationRepository(JsonRepository):
    '''The configuration repository handle CRUD projects in the
    configuration path
    '''
    # save projects in the configuration directory
    name = 'configuration.json'
    of_type = Project
    pathfile = 'configuration.txt'

    def __init__(self, path=None):
        # load last path from file
        filename = type(self).pathfile
        if os.path.exists(filename):
            with open(filename) as f:
                path = f.read()

        if not path or not os.path.exists(path):
            path = self.default_path()

        super().__init__(path)

    def get(self):
        '''Returns a collection of projects setting the name'''
        projects = super().get()
        for project in projects:
            project.name = self.get_basename(project.path)

        return projects

    def get_selected(self):
        '''Returns the selected project if there is,
        else returns a new instance of project model
        '''
        selected = self.first(lambda p: p.selected)
        return selected if selected else Project()

    def default_path(self):
        '''Returns a default path for configuration folder'''
        return os.path.join(self.get_home_path(), 'templatizator')

    @classmethod
    def get_home_path(cls):
        '''Get home path'''
        return os.path.expanduser('~')

    def get_project_path(self):
        '''Returns the path of selected project if there is'''
        if self.path:
            selected = self.get_selected()
            if selected and selected.path_name:
                return os.path.join(self.path, selected.path_name)

        return None

    def find_node(self, node, path):
        '''Find node instance inside the node graph informed by the path'''
        if node.path == path:
            return node

        for child in node.children:
            if child.path == path:
                return child

            if child.children:
                child_of = self.find_node(child, path)
                if child_of is not None:
                    return child_of
        return None

    def get_filetree(self):
        '''Get filetree graph of selected project'''
        parent = self.get_selected()
        if not parent.path:
            return parent
        parent.name = self.get_basename(parent.path)

        # Variable files is necessary to run loop walk
        # pylint: disable=unused-variable
        for root, directories, files in os.walk(parent.path):
            node = self.find_node(parent, root)

            for directory in directories:
                path = os.path.join(root, directory)
                node.add_child(Directory(path, directory))

        return parent

    def change_project(self, path):
        '''When the project path is changed we create and select it if isn't
        exists, else just select the project and save into the project
        collection.
        '''
        projects = self.get()
        project = self.first(lambda p: p.path == path, projects)

        # unselect projects
        for proj in projects:
            proj.selected = False

        if not project:
            # add new project

            # set friendly project name
            path_name = self.get_basename(path)
            name = path_name
            i = 0
            while self.first(lambda p: p.name == path_name):
                i += 1
                path_name = f'{name}-{i}'
            project = Project(path, name, path_name, True)
            projects.append(project)
        else:
            # project already exist, select project
            project.selected = True

        self.save(projects)

        local_path = os.path.join(self.path, project.path_name)

        return local_path

    def change_path(self, path):
        with open(type(self).pathfile, 'w') as f:
            f.write(path)
        self.path = path


class VariableRepository(JsonRepository):
    '''Handle CRUD variables'''
    # save variables json
    name = 'variables.json'
    of_type = Variable


class TemplateRepository(NodeRepository):
    '''Handle CRUD Templates'''
    # save json templates
    name = 'templates.json'
    of_type = Template


class TemplateFileRepository(FileRepository):
    '''Handle CRUD templates text file from hard drive'''
    # save template files
    pass


class ConfigurableRepository(NodeRepository):
    '''Handle CRUD Configurable files'''
    # save configurable files json
    name = 'configurablefiles.json'
    of_type = ConfigurableFile

    def is_child(self, parent_path, filename):
        '''Verify if filename is a existent file into the parent_path folder'''
        return (os.path.exists(os.path.join(parent_path, filename)) and
                self.get_parent_path(filename) == parent_path)


class ConfigurableFileRepository(FileRepository):
    '''Handle CRUD configurable text file from hard drive'''
    # save configurable files
    pass
