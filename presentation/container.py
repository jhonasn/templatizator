from domain.container import Container
from presentation.window import Window
from presentation.variables import Variables
from presentation.editor import Editor

class Container:
    def configure(builder):
        Container.variables = Variables(builder, Container.variables_application)
        Container.editor = Editor(builder, Container.template_application)
        Container.window = Window(builder, self.variables, self.editor, Container.project_application)

