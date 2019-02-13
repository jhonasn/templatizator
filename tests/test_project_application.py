from os.path import join, basename, exists
from pytest import fixture, raises, mark
from templatizator.domain.container import Container
from templatizator.domain.infrastructure import ProjectNotSet
from tests import configuration_path, project_path, configure_paths, \
    delete_configuration_folders

project_directories = ['domain', 'repository', 'service', 'application']


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
