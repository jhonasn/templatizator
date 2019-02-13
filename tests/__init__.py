from os.path import join, exists
from os import makedirs
from shutil import rmtree
from json import dumps
from templatizator.domain.container import Container

Container.configure()
configuration_path = join(Container.project_application.home_path,
    'tests_templatizator')
project_path = join(Container.project_application.home_path, 'test_project')

def set_configuration_path():
    Container.project_application.change_configuration_path(configuration_path)

def set_project_path():
    create_test_project()
    Container.project_application.change_path(project_path)

def configure_paths():
    set_configuration_path()
    set_project_path()

def delete_configuration_folders():
    rmtree(Container.project_application.configuration_path, ignore_errors=True)
    rmtree(configuration_path, ignore_errors=True)
    rmtree(project_path, ignore_errors=True)
    return (
        not exists(Container.project_application.configuration_path)
        and not exists(configuration_path)
    )

def create_file(path, content):
    if not exists(path):
        with open(path, 'w') as f:
            f.write(content)

def create_test_project():
    makedirs(join(project_path, 'domain'), exist_ok=True)
    makedirs(join(project_path, 'repository'), exist_ok=True)
    makedirs(join(project_path, 'service'), exist_ok=True)
    makedirs(join(project_path, 'application'), exist_ok=True)
    configurable_file = join(project_path, 'package.json')
    configurable_content = dumps({'name': 'Test project', 'version': '1.0.0'})
    fake_configurable_file = join(project_path, 'application', 'package.json')
    create_file(configurable_file, configurable_content)
    create_file(fake_configurable_file, configurable_content)
    configurable_file = join(project_path, 'multiline_package.json')
    configurable_content = dumps({'name': 'Test project', 'version': '1.0.0'},
                                    indent=2)
    create_file(configurable_file, configurable_content)

def teardown_module(module):
    delete_configuration_folders()
