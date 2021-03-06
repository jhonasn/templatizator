'''Container module that instantiate classes to accomplish IoC role'''
from templatizator.domain.container import Container as DomainContainer
from templatizator.presentation.window import Window
from templatizator.presentation.variables import Variables
from templatizator.presentation.editor import Editor
from templatizator.presentation.configurable_editor import ConfigurableEditor


# pylint: disable=too-few-public-methods
class Container:
    '''Static container class that instantiate GUI handlers with application
    layer instances
    '''
    def __init__(self):
        raise Exception('Static class is not instantiable')

    @classmethod
    def configure(cls, builder):
        '''Instantiate GUI handler classes'''
        Container.variables = Variables(
            builder,
            DomainContainer.variable_application
        )
        Container.editor = Editor(
            builder,
            DomainContainer.template_application,
            DomainContainer.variable_application
        )
        Container.configurable_editor = ConfigurableEditor(
            builder,
            DomainContainer.configurable_file_application,
            DomainContainer.variable_application,
            DomainContainer.template_application
        )
        Container.window = Window(
            builder,
            Container.variables,
            Container.editor,
            Container.configurable_editor,
            DomainContainer.project_application,
            DomainContainer.template_application,
            DomainContainer.configurable_file_application
        )
