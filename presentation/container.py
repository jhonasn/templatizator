'''Container module that instantiate classes to accomplish IoC role'''
from domain.container import Container as DomainContainer
from presentation.window import Window
from presentation.variables import Variables
from presentation.editor import Editor


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
        Container.variables = Variables(builder,
                                        DomainContainer.variable_application)
        Container.editor = Editor(builder,
                                  DomainContainer.template_application,
                                  DomainContainer.variable_application)
        Container.window = Window(
            builder, Container.variables, Container.editor,
            DomainContainer.project_application,
            DomainContainer.template_application,
            DomainContainer.configurable_file_application)
