from os.path import join, basename, dirname, exists
from json import dumps
from pytest import fixture, raises, mark
from templatizator.domain.container import Container
from templatizator.domain.infrastructure import ProjectNotSet, \
    RepositoryPathNotSet
from tests import configuration_path, project_path, \
    delete_configuration_folders, set_configuration_path, configure_paths


def teardown_module(module):
    delete_configuration_folders()

project_directories = ['domain', 'repository', 'service', 'application']
templates_add = [
    {'directory': 'application', 'file': '[name]_application.[ext]'},
    {'directory': 'service', 'file': '[name]_service.[ext]'},
    {'directory': 'repository', 'file': '[name]_repository.[ext]'},
    {'directory': 'domain', 'file': '[name].[ext]'}
]

class TestVariableApplication:
    '''Test variable application api'''
    @staticmethod
    def add_variables():
        var_app = Container.variable_application
        var_app.add('name', 'person')
        if not any(filter(lambda v: v.name == 'ext', var_app.get())):
            Container.variable_application.add('ext', 'py')

    @fixture
    def application(self):
        configure_paths()
        application = Container.variable_application
        for var in application.get():
            application.remove(var.name)
        return application

    @fixture
    def variables(self, application):
        application.add('test_var', 'var_value')
        application.add('variable_one', 'variable one')
        application.add('variable_2', 'variable two')
        return application.get()

    def test_get(self, application):
        '''Test get method'''
        variables = application.get()
        assert len(variables) == 0

    def test_add(self, variables):
        assert len(variables) == 3
        name = variables[0].name
        value = variables[0].value
        assert name == 'test_var' and value == 'var_value'
        name = variables[1].name
        value = variables[1].value
        assert name == 'variable_one' and value == 'variable one'
        name = variables[2].name
        value = variables[2].value
        assert name == 'variable_2' and value == 'variable two'

    def test_change(self, application, variables):
        name = variables[0].name
        assert name == 'test_var'
        newname, newvalue = 'new_test_var', 'new test var content'
        application.change(name, newname, newvalue)
        var = application.get()[0]
        assert var.name == newname and var.value == newvalue

    def test_remove(self, application, variables):
        name = variables[0].name
        assert name == 'test_var'
        assert len(variables) == 3
        application.remove(name)
        vars = application.get()
        assert len(vars) == 2
        assert name not in map(lambda v: v.name in vars, vars)

    def test_project_not_selected(self, application):
        delete_configuration_folders()
        set_configuration_path()
        filetree = Container.project_application.get()
        with raises(ProjectNotSet):
            application.add('test', 'without project set')


class TestProjectApplication:
    @fixture
    def application(self):
        configure_paths()
        app = Container.project_application
        app.change_path(project_path)
        return app

    def teardown_method(self, method):
        from shutil import rmtree
        delete_configuration_folders()
        path = 'tests_templatizator'
        home_path = Container.project_application.home_path
        rmtree(join(home_path, path), ignore_errors=True)
        rmtree(join(home_path, path + '_proj'), ignore_errors=True)
        rmtree(join(home_path, path + '_one'), ignore_errors=True)
        rmtree(join(home_path, path + '_one_proj'), ignore_errors=True)
        rmtree(join(home_path, path + '_other'), ignore_errors=True)
        rmtree(join(home_path, path + '_other_proj'), ignore_errors=True)
        rmtree(join(home_path, 'tests_other_config'), ignore_errors=True)

    @mark.parametrize('path', [
        'tests_templatizator_one',
        'tests_templatizator',
        'tests_templatizator_other',
    ])
    def test_reload_configuration_project(self, path):
        app = Container.project_application
        path = join(app.home_path, path)

        old_conf = app.configuration_path
        old_proj = app.get().path

        app.change_configuration_path(path)
        path = join(app.home_path, path + '_proj')
        app.change_path(path)

        assert app.configuration_path != old_conf
        assert app.get().path != old_proj

        old_conf = app.configuration_path
        old_proj = app.get().path

        Container.configure()

        # restart
        app = Container.project_application

        assert app.configuration_path == old_conf
        assert app.get().path == old_proj

    @mark.parametrize('name', project_directories)
    def test_get(self, application, name):
        path = project_path
        filetree = application.get()

        assert filetree.path == path
        assert filetree.name == basename(path)

        folder = list(filter(lambda f: f.name == name, filetree.children))
        assert bool(folder)
        assert folder[0].path == join(path, name)

    def test_change_path_same_project_name(self, application):
        from json import loads
        var_app = Container.variable_application

        pathname = 'tests_templatizator_one_proj'
        path = join(application.home_path, pathname)
        application.change_path(path)

        def get_project(path):
            projects = None
            with open(join(
                application.configuration_path, 'configuration.json'
            )) as f:
                projects = loads(f.read())
            project = list(filter(lambda p: p['path'] == path, projects))
            any(project)
            return project[0]

        is_project_variables_exist = lambda p: exists(join(
            application.configuration_path, p['path_name'], 'variables.json'
        ))

        project = get_project(path)

        var_app.add('test', 'test value')

        assert exists(join(
            application.configuration_path, project['path_name']
        ))
        assert is_project_variables_exist(project)

        first_project_name = project['path_name']

        path = join(application.home_path, 'tests_templatizator_other_proj',
                    pathname)
        application.change_path(path)

        project = get_project(path)

        var_app.add('test_other', 'other project test')

        assert exists(join(
            application.configuration_path, project['path_name']
        ))
        assert is_project_variables_exist(project)
        assert project['path_name'] != first_project_name

    def test_change_configuration_path(self, application):
        app = Container.project_application
        path = join(app.home_path, 'tests_other_config')
        app.change_configuration_path(path)
        app.change_path(project_path)
        saved_path = None
        from templatizator.domain.repository import ConfigurationRepository
        with open(ConfigurationRepository.pathfile) as f:
            saved_path = f.read()
        assert saved_path == path
        assert exists(path)
        assert exists(join(path, 'configuration.json'))

    def test_home_path(self, application):
        from os.path import expanduser
        assert application.home_path == expanduser('~')

    @mark.parametrize('name', project_directories)
    def test_find_node(self, application, name):
        from templatizator.domain.domain import Directory
        filetree = application.get()
        path = join(project_path, name)
        node = application.find_node(filetree, path)
        assert type(node) is Directory
        assert node.name == name and node.path == path

    def test_save_into_project_not_set(self):
        with raises(ProjectNotSet):
            Container.project_application.save_into_project()

    # def test_save_into_project(self):
    # implemented in template and configuration tests

class FileApplicationTestHelper:
    @staticmethod
    def test_create_child(application, file_nodes):
        for file_node in file_nodes:
            child = application.create_child(file_node, 'child')
            assert child.name == 'child'
            assert child.path == join(file_node.path, 'child')

    @staticmethod
    def test_save(application, file_nodes, get_all):
        for file_node in file_nodes:
            new_name = file_node.name + '_changed'
            file_node.name = new_name
            path = join(dirname(file_node.path), new_name)
            application.save(file_node)
            assert file_node.name == new_name
            assert file_node.path == path
            file_node = list(filter(lambda t: t.name == new_name, get_all()))
            assert any(file_node)
            file_node = file_node[0]
            assert file_node.name == new_name
            assert file_node.path == path

    @staticmethod
    def test_save_file(application, file_nodes, get_all):
        for file_node in file_nodes:
            new_name = file_node.name + '_changed'
            path = join(dirname(file_node.path), new_name)
            new_content = f'path: {path}'
            application.save_file(file_node, new_name, new_content)
            file_node = list(filter(lambda t: t.name == new_name, get_all()))
            assert any(file_node)
            file_node = file_node[0]
            assert file_node.name == new_name
            assert file_node.path == path
            content = application.get(file_node)
            assert content == new_content

    @staticmethod
    def test_remove(application, templates, get_all):
        for template in templates:
            assert any(filter(lambda t: t.name == template.name, get_all()))
            application.remove(template)
            assert not any(filter(lambda t: t.name == template.name, get_all()))


class TestTemplateApplication:
    @classmethod
    def setup_method(cls):
        delete_configuration_folders()

    @staticmethod
    def add_templates():
        from templatizator.domain.domain import Template

        for template in templates_add:
            directory, name = template.values()
            path = join(project_path, directory, name)
            content = f'''class {name}_{directory}:
                def __init__(self):
                    self.is_{directory} = True
            '''
            Container.template_application.add(Template(path, name), content)

    @fixture
    def application(self):
        configure_paths()
        TestVariableApplication.add_variables()
        return Container.template_application

    @fixture
    def templates(self, application):
        TestTemplateApplication.add_templates()
        return application.get_all()

    @mark.parametrize('added_template', templates_add)
    def test_get_all(self, templates, added_template):
        assert len(templates) == 4
        assert any(filter(lambda t: t.name == added_template['file'], templates))

    def test_get(self, application, templates):
        for template in templates:
            content = application.get(template)
            lines = content.splitlines()
            directory = list(filter(lambda t: t['file'] == template.name,
                                    templates_add))[0]['directory']
            assert len(lines) == 4
            assert lines[0] == f'class {template.name}_{directory}:'

    def test_create_child(self, application, templates):
        FileApplicationTestHelper.test_create_child(application, templates)

    def test_save(self, application, templates):
        FileApplicationTestHelper.test_save(application, templates,
                                            application.get_all)

    def test_save_file(self, application, templates):
        FileApplicationTestHelper.test_save_file(application, templates,
                                                    application.get_all)

    def test_remove(self, application, templates):
        FileApplicationTestHelper.test_remove(application, templates,
                                                application.get_all)

    def test_get_path(self, application, templates):
        for template in templates:
            path = application.get_path(template)
            assert path == join(
                Container.project_application.configuration_path,
                basename(project_path), template.name)

            # verify if getting path is not changing the repository path
            templates = application.get_all()
            assert len(templates) == 4

    def test_save_into_project(self, application, templates):
        Container.project_application.save_into_project()
        variables = Container.variable_application.get()
        for template in templates:
            name = template.name
            content = application.get(template)
            directory = list(filter(lambda t: t['file'] == template.name,
                                    templates_add))[0]['directory']
            for var in variables:
                placeholder = f'[{var.name}]'
                name = name.replace(placeholder, var.value)
                content = content.replace(placeholder, var.value)
            path = join(project_path, directory, name)
            assert exists(path)
            assert content.splitlines()[0] == f'class {name}_{directory}:'

    # def test_add(self):
    # already tested in templates fixture


class TestConfigurableApplication:
    initial_configurable_content = dumps({'name': 'Test project', 'version': '1.0.0'})

    @classmethod
    def setup_method(cls):
        delete_configuration_folders()

    @staticmethod
    def get_configurable():
        from templatizator.domain.domain import ConfigurableFile
        path = join(project_path, 'package.json')
        return ConfigurableFile(path)

    @fixture
    def application(self):
        configure_paths()
        TestVariableApplication.add_variables()
        TestTemplateApplication.add_templates()
        return Container.configurable_file_application

    @fixture
    def repository(self):
        from templatizator.domain.repository import ConfigurableRepository
        repository = ConfigurableRepository()
        repository.path = join(Container.project_application.configuration_path,
                                basename(project_path))
        return repository

    @fixture
    def configurables(self, application, repository):
        content = dumps({
            'name': 'Test project', 'version': '1.0.0',
            'files': ['template.All.name'], 'paths': ['template.All.path'],
            'relative_paths': ['template.All.relative_path']
        })
        configurable = TestConfigurableApplication.get_configurable()
        configurable.name = application.get_filename(configurable.path)
        application.add(configurable, content)
        return repository.get()

    def test_get(self, application):
        content = application.get(
            TestConfigurableApplication.get_configurable())
        assert content == \
            TestConfigurableApplication.initial_configurable_content

    def test_get_created(self, application, configurables):
        content = application.get(configurables[0])
        assert content != \
            TestConfigurableApplication.initial_configurable_content

    def test_create_child(self, application, configurables):
        FileApplicationTestHelper.test_create_child(application, configurables)

    def test_save(self, application, repository, configurables):
        FileApplicationTestHelper.test_save(application, configurables,
                                            repository.get)

    def test_save_file(self, application, repository, configurables):
        FileApplicationTestHelper.test_save_file(application, configurables,
                                                    repository.get)

    def test_remove(self, application, repository, configurables):
        FileApplicationTestHelper.test_remove(application, configurables,
                                                repository.get)

    def test_get_filename(self, application, configurables):
        assert configurables[0].name == 'package.json'

    def test_is_child(self, application, configurables):
        configurable = configurables[0]
        assert application.is_child(project_path, configurable.path)
        assert not application.is_child(dirname(project_path),
                                                configurable.path)
        assert not application.is_child(join(project_path, 'application'),
                                                configurable.path)

    # def test_save_into_project(self):

    # def test_add(self):
    # already testes on configurables fixture
