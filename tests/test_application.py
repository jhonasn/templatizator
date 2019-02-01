from os.path import join, basename
from pytest import fixture, raises, mark
from templatizator.domain.container import Container
from templatizator.domain.infrastructure import ProjectNotSet, \
    RepositoryPathNotSet
from tests import configuration_path, project_path, \
    delete_configuration_folders, set_configuration_path, configure_paths


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
        return Container.project_application

    @classmethod
    def teardown_class(cls):
        from shutil import rmtree
        path = 'tests_templatizator'
        home_path = Container.project_application.home_path
        rmtree(join(home_path, path), ignore_errors=True)
        rmtree(join(home_path, path + '_one'), ignore_errors=True)
        rmtree(join(home_path, path + '_another'), ignore_errors=True)

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

    @mark.parametrize('name', [
        'domain', 'repository', 'service', 'application'
    ])
    def test_get(self, application, name):
        path = project_path
        filetree = application.get()

        assert filetree.path == path
        assert filetree.name == basename(path)

        folder = list(filter(lambda f: f.name == name, filetree.children))
        assert bool(folder)
        assert folder[0].path == join(path, name)

    # def test_change_path_same_project_name(self):
    # def test_change_configuration_path(self):
    # def test_home_path(self):
    # def test_find_node(self):
    # def test_save_into_project(self):


class TestTemplateApplication:
    @fixture
    def application(self):
        return Container.template_application

    # def test_get(self):
    # def test_add(self):
    # def test_create_child(self):
    # def test_save(self):
    # def test_save_file(self):
    # def test_(self):
    # def test_remove(self):
    # def test_get_path(self):
    # def test_get_all(self):


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
