from domain.repository import *
from domain.service import *
from domain.application import *
from domain.helper import Event

class Container:
    def configure():
        event = Event('project_changed')

        configuration_repository = ConfigurationRepository()
        variable_repository = VariableRepository(configuration_repository.path)
        template_repository = TemplateRepository(configuration_repository.path)
        template_file_repository = TemplateFileRepository(configuration_repository.path)
        configurable_repository = ConfigurableRepository(configuration_repository.path)
        configurable_file_repository = ConfigurableFileRepository(configuration_repository.path)

        configuration_service = ConfigurationService(configuration_repository)
        project_service = ProjectService(configuration_repository, variable_repository,
                template_repository, configurable_repository,
                template_file_repository, configurable_file_repository, event)
        variable_service = VariableService(variable_repository, event)
        template_service = TemplateService(template_file_repository, template_repository, event)
        configurable_service = ConfigurableService(configurable_file_repository, configurable_repository, event)

        Container.project_application = ProjectApplication(project_service, configuration_service)
        Container.variable_application = VariableApplication(variable_service)
        Container.template_application = TemplateApplication(template_service)
        Container.configurable_file_application = ConfigurableFileApplication(configurable_service)

