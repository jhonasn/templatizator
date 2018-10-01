from domain.repository import *
from domain.service import *
from domain.application import *

class Container:
    def configure():
        configuration_repository = ConfigurationRepository()
        project_repository = ProjectRepository()
        variables_repository = VariablesRepository()
        template_repository = TemplateRepository()
        configurable_file_repository = ConfigurableFileRepository()

        configuration_service = ConfigurationService(configurationRepository)
        project_service = ProjectService(projectRepository, configurationRepository)
        variables_service = VariablesService(variablesRepository)
        template_service = TemplateService(templateRepository)
        configurable_file_service = ConfigurableFileService(configurableFileRepository)

        Container.project_application = ProjectApplication(projectService, configurationService)
        Container.variables_application = VariablesApplication(variablesService)
        Container.template_application = TemplateApplication(templateService)
        Container.configurable_file_application = ConfigurableFileApplication(configurableFileService)

