from os.path import join, basename, exists
from pytest import fixture, mark
from templatizator.domain.container import Container
from tests import configuration_path, project_path, configure_paths, \
    delete_configuration_folders, create_test_project
from tests.file_application_test_helper import FileApplicationTestHelper
from tests.test_variable_application import add_variables

templates_add = [
    {'directory': 'application', 'file': '[name]_application.[ext]'},
    {'directory': 'service', 'file': '[name]_service.[ext]'},
    {'directory': 'repository', 'file': '[name]_repository.[ext]'},
    {'directory': 'domain', 'file': '[name].[ext]'}
]


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


class TestTemplateApplication:
    @classmethod
    def setup_method(cls):
        delete_configuration_folders()

    def get_templates():
        templates = Container.template_application.get_all()
        if not templates:
            add_templates()
            templates = Container.template_application.get_all()
        return templates

    @fixture
    def application(self):
        configure_paths()
        add_variables()
        return Container.template_application

    @fixture
    def templates(self, application):
        add_templates()
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

    def test_not_save_into_project(self, application, templates):
        def get_directory(template):
            return list(filter(lambda t: t['file'] == template.name,
                                         templates_add))[0]['directory']

        variables = Container.variable_application.get()
        FileApplicationTestHelper.test_not_save_into_project(application,
            templates, variables,
            Container.project_application.save_into_project, get_directory)

    # def test_add(self):
    # already tested in templates fixture
