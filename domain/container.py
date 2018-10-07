'''Container module that instantiate classes to accomplish IoC role'''
from domain.repository import ConfigurationRepository, VariableRepository, \
    TemplateRepository, TemplateFileRepository, \
    ConfigurableRepository, ConfigurableFileRepository
from domain.service import ProjectService, ConfigurationService, \
    VariableService, TemplateService, ConfigurableService
from domain.application import ProjectApplication, VariableApplication, \
    TemplateApplication, ConfigurableFileApplication
from domain.helper import Event

class Container:
    @classmethod
    def configure(cls):
        '''Instantiate events, and DDD layers'''
        # events
        project_changed_event = Event()
        configuration_changed_event = Event()

        # repository layer
        configuration_repository = ConfigurationRepository()
        variable_repository = VariableRepository()
        template_repository = TemplateRepository()
        template_file_repository = TemplateFileRepository()
        configurable_repository = ConfigurableRepository()
        configurable_file_repository = ConfigurableFileRepository()

        # service layer
        # the order affects the event subscribe and publish into the services
        variable_service = VariableService(
            variable_repository,
            project_changed_event)
        template_service = TemplateService(
            template_file_repository,
            template_repository,
            project_changed_event)
        configurable_service = ConfigurableService(
            configurable_file_repository, configurable_repository,
            project_changed_event)
        project_service = ProjectService(
            configuration_repository, variable_repository, template_repository,
            configurable_repository, template_file_repository,
            configurable_file_repository, configuration_changed_event,
            project_changed_event)
        configuration_service = ConfigurationService(
            configuration_repository,
            configuration_changed_event)

        # application layer
        Container.project_application = ProjectApplication(
            project_service,
            configuration_service)
        Container.variable_application = VariableApplication(variable_service)
        Container.template_application = TemplateApplication(template_service)
        Container.configurable_file_application = ConfigurableFileApplication(
            configurable_service)
