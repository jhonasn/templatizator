from domain.container import Container as DomainContainer
from presentation import Window, Variables, Editor

class Container:
    def configure(builder):
        Container.variables = Variables(builder, DomainContainer.variable_application)
        Container.editor = Editor(builder, DomainContainer.template_application)
        Container.window = Window(builder, Container.variables, Container.editor, DomainContainer.project_application)

