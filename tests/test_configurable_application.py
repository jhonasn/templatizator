from os.path import join, basename, dirname, exists
from json import dumps
from pytest import fixture
from templatizator.domain.container import Container
from tests import configuration_path, project_path, configure_paths, \
    delete_configuration_folders
from tests.file_application_test_helper import FileApplicationTestHelper
from tests.test_variable_application import add_variables
from tests.test_template_application import add_templates


class TestConfigurableApplication:
    initial_configurable_content_object = {'name': 'Test project',
                                            'version': '1.0.0'}
    configurable_content_object = {'name': 'Test project', 'version': '1.0.0',
        'files': ['[template.All.name]'], 'paths': ['[template.All.path]'],
        'relative_paths': ['[template.All.relative_path]']}

    @classmethod
    def setup_method(cls):
        delete_configuration_folders()

    @staticmethod
    def get_configurables():
        from templatizator.domain.domain import ConfigurableFile
        path = join(project_path, 'package.json')
        path2 = join(project_path, 'multiline_package.json')
        return [ConfigurableFile(path), ConfigurableFile(path2)]

    @fixture
    def application(self):
        configure_paths()
        add_variables()
        add_templates()
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
        obj = TestConfigurableApplication.configurable_content_object
        configurables = TestConfigurableApplication.get_configurables()
        for configurable in configurables:
            configurable.name = application.get_filename(configurable.path)

            content = dumps(obj, indent=2 \
                if configurable.name == 'multiline_package.json' else None)

            # apply inline template
            # and add comma at the end of template lines on multiline_package
            sufix = ','
            prefix = ''
            template = '{}"[template.All.{}]"{}'
            replace = lambda prop: content.replace(
                template.format('', prop, ''),
                template.format(prefix, prop, sufix))

            if configurable.name == 'package.json':
                sufix = ', ]>'
                prefix = '<['

            content = replace('name')
            content = replace('path')
            content = replace('relative_path')

            application.add(configurable, content)
        return repository.get()

    def test_get(self, application):
        for configurable in TestConfigurableApplication.get_configurables():
            content = application.get(configurable)
            obj = TestConfigurableApplication.\
                initial_configurable_content_object
            content_result = dumps(obj, indent=2 \
                if basename(configurable.path) == 'multiline_package.json' \
                else None)
            assert content == content_result

    def test_get_created(self, application, configurables):
        for configurable in configurables:
            content = application.get(configurable)
            init_obj = TestConfigurableApplication.\
                        initial_configurable_content_object
            content_result = dumps(init_obj, indent=2 \
                if configurable.name == 'multiline_package.json' else None)
            assert content != content_result

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
        assert configurables[1].name == 'multiline_package.json'

    def test_is_child(self, application, configurables):
        for configurable in configurables:
            assert exists(configurable.path)
            assert exists(join(project_path, configurable.name))
            assert application.is_child(project_path, configurable.path)
            assert not application.is_child(dirname(project_path),
                                                    configurable.path)
            assert not application.is_child(join(project_path, 'application'),
                                                    configurable.path)

    def test_save_into_project(self, application, configurables):
        Container.project_application.save_into_project()

        expected_content = f'''{{
  "name": "[pname]",
  "version": "1.0.0",
  "files": [
    "person_application.py",
    "person_service.py",
    "person_repository.py",
    "person.py",
    <["[template.All.name]", ]>
  ],
  "paths": [
    "[path]\\application\\person_application.py",
    "[path]\\service\\person_service.py",
    "[path]\\repository\\person_repository.py",
    "[path]\\domain\\person.py",
    <["[template.All.path]", ]>
  ],
  "relative_paths": [
    "application\\person_application.py",
    "service\\person_service.py",
    "repository\\person_repository.py",
    "domain\\person.py",
    <["[template.All.relative_path]", ]>
  ]
}}'''
        expected_content_inline = expected_content.replace('\n', '')\
            .replace(' ', '').replace(':', ': ').replace(',', ', ')
        expected_content = expected_content.replace('[pname]', 'Test project')
        expected_content = expected_content.replace('[path]', project_path)
        expected_content_inline = expected_content_inline\
            .replace('[pname]', 'Test project')
        expected_content_inline = expected_content_inline\
            .replace('[path]', project_path)
        expected_content = expected_content.replace('<[', '').replace(' ]>', '')

        from re import sub

        for configurable in configurables:
            path = join(project_path, configurable.name)
            assert exists(path)
            is_inline = configurable.name == 'package.json'

            content = application.get(configurable)

            content_result = expected_content_inline if is_inline \
                                                    else expected_content

            # test configurable template content
            assert content == content_result

            with open(path) as f:
                content = f.read()

            # remove inline template
            regex = r'\<\[.*?\]\>' if is_inline else r'\n.*?\[.*?\].*?\n'
            replacement = '' if is_inline else '\n'
            content_result = sub(regex, lambda m: replacement, content_result)

            # test configurable content result in project
            assert content == content_result

    def test_not_save_into_project(self, application, configurables):
        variables = Container.variable_application.get()
        FileApplicationTestHelper.test_not_save_into_project(application,
            configurables, variables,
            Container.project_application.save_into_project)

    # def test_add(self):
    # already tested on configurables fixture
