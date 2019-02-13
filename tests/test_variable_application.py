from pytest import fixture, raises
from templatizator.domain.container import Container
from templatizator.domain.infrastructure import ProjectNotSet
from tests import delete_configuration_folders, configure_paths, \
    set_configuration_path


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
