from os.path import join
from templatizator.domain.container import Container

def setup_function():
    Container.configure()
    test_path = Container.project_application.home_path
    test_path = join(test_path, 'tests_templatizator')
    if Container.project_application.configuration_path != test_path:
        Container.project_application.change_configuration_path(test_path)
    print('setup function executed', test_path)

setup_function()
