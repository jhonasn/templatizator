from os.path import join, basename, exists
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

    # def test_save_into_project(self):
    # implemented in template and configuration tests


class TestTemplateApplication:
    @classmethod
    def setup_method(cls):
        app = Container.template_application
        for template in app.get_all():
            app.remove(template)
        Container.variable_application.remove('name')
        Container.variable_application.remove('ext')

    @fixture
    def application(self):
        configure_paths()
        var_app = Container.variable_application
        var_app.add('name', 'person')
        if not any(filter(lambda v: v.name == 'ext', var_app.get())):
            Container.variable_application.add('ext', 'py')
        return Container.template_application

    @fixture
    def templates(self, application):
        from templatizator.domain.domain import Template

        for template in templates_add:
            directory, name = template.values()
            path = join(project_path, directory, name)
            content = f'''class {name}:
                def __init__(self):
                    self.is_{directory} = True
            '''
            application.add(Template(path, name), content)

        return application.get_all()

    @mark.parametrize('added_template', templates_add)
    def test_get_all(self, templates, added_template):
        assert len(templates) == 4
        assert any(filter(lambda t: t.name == added_template['file'], templates))

    # def test_get(self, templates, added_template):
    # def test_create_child(self):
    # def test_save(self):
    # def test_save_file(self):
    # def test_remove(self):
    # def test_get_path(self):
    # def test_save_into_project(self):


class TestConfigurableApplication:
    @fixture
    def application(self):
        return Container.configurable_file_application

    # def test_get(self):
    # def test_add(self):
    # def test_create_child(self):
    # def test_save(self):
    # def test_save_file(self):
    # def test_(self):
    # def test_remove(self):
    # def test_get_filename(self):
    # def test_is_child(self):
    # def test_save_into_project(self):
