'''Service layer module'''
from abc import ABC
from templatizator.domain.domain import Variable
from templatizator.domain.infrastructure import ProjectNotSet
from templatizator.domain.helper import OS


class ConfigurationService:
    '''Handle configuration rules'''
    def __init__(self, repository, configuration_changed_event):
        self.repository = repository
        self.event = configuration_changed_event

    def change_path(self, path):
        '''Changes repository path and notify it through event'''
        # save configuration path
        self.repository.change_path(path)
        self.event.publish(path)

    def get_path(self):
        '''Returns configuration path'''
        return self.repository.path


class ProjectService:
    '''Handle project rules'''
    # Project has no repository so its not necessary to call base class
    # pylint: disable=super-init-not-called,too-many-arguments
    def __init__(self, configuration_repository, variable_repository,
                 template_repository, configurable_repository,
                 template_file_repository, configurable_file_repository,
                 configuration_changed_event, project_change_event):
        self.configuration_repository = configuration_repository
        self.variable_repository = variable_repository
        self.template_repository = template_repository
        self.configurable_repository = configurable_repository
        self.template_file_repository = template_file_repository
        self.configurable_file_repository = configurable_file_repository
        self.event = project_change_event

        configuration_changed_event.subscribe(self.configuration_changed)

        path = self.configuration_repository.get_project_path()
        if path:
            self.event.publish(path)

    def get_home_path(self):
        '''Get home path'''
        return self.configuration_repository.get_home_path()

    def change_path(self, path):
        '''Changes repository path and notify it through event'''
        project_path = self.configuration_repository.change_project(path)
        self.event.publish(project_path)

    def configuration_changed(self, path):
        '''Configuration path change listener, change path when receives a
        notification from configuration and notify other services through event
        '''
        self.configuration_repository.path = path
        path = self.configuration_repository.get_project_path()
        self.event.publish(path)

    def find_node(self, filetree, path):
        '''Find node instance of informed path into the filetree'''
        return self.configuration_repository.find_node(filetree, path)

    def get_filetree(self):
        '''Get filetree graph and fills it with templates and configurables'''
        filetree = self.configuration_repository.get_filetree()

        templates = self.template_repository.get()
        configurables = self.configurable_repository.get()

        for template in templates:
            parent = self.find_node(
                filetree,
                self.configuration_repository.get_parent_path(template.path)
            )
            if parent:
                parent.add_child(template)

        for configurable in configurables:
            parent = self.find_node(
                filetree,
                self.configuration_repository.get_parent_path(
                    configurable.path
                )
            )
            if parent:
                parent.add_child(configurable)

        return filetree

    def replace_variables(self, text):
        '''Replaces placeholders in the passed text with
        recorded application variables
        '''
        new_text = text
        for var in self.variable_repository.get():
            new_text = new_text.replace(f'[{var.name}]', var.value)

        return new_text

    def save_into_project(self):
        '''Save configured templates and configurables
        into the project folder
        '''
        local_path = self.configuration_repository.get_project_path()
        if not local_path:
            raise ProjectNotSet

        # save templates into the project
        prev_name = self.template_file_repository.name
        for template in self.template_repository.get():
            if template.save:
                self.template_file_repository.path = local_path
                self.template_file_repository.name = template.name

                content = self.template_file_repository.get()
                content = self.replace_variables(content)

                self.template_file_repository.path = \
                    self.configuration_repository.get_parent_path(template.path)
                self.template_file_repository.name = \
                    self.replace_variables(template.name)
                self.template_file_repository.save(content)

        self.template_file_repository.path = local_path
        self.template_file_repository.name = prev_name

        # save configurable files into the project
        prev_name = self.configurable_file_repository.name
        for configurable in self.configurable_repository.get():
            from re import sub
            if configurable.save:
                self.configurable_file_repository.path = local_path
                self.configurable_file_repository.name = configurable.name

                content = self.configurable_file_repository.get()
                templates = self.template_repository.get()

                # first remount content replacing template.All placeholders
                # by each template
                new_content = ''
                template_all_props = ['name', 'path', 'relative_path']
                for line in content.splitlines():
                    props = map(lambda p: f'[template.All.{p}]', template_all_props)
                    if any(filter(lambda p: p in line, props)):
                        prev_line = line

                        for template in templates:
                            for prop in template_all_props:
                                line = line.replace(
                                    f'[template.All.{prop}]',
                                    f'[template.{template.name}.{prop}]'
                                )

                            # place the template line again bellow the line
                            line += f'\n{prev_line}'

                    new_content += f'{line}\n'

                content = new_content

                # replace templates on content
                project_path = self.get_filetree().path
                for index, template in enumerate(templates):
                    template_replace = {
                        'name': self.replace_variables(template.name),
                        'path': self.replace_variables(OS.get_default_path(
                            template.path
                        )),
                    }
                    template_replace['relative_path'] = \
                        template_replace['path'].replace(project_path, '')
                    # remove first slash
                    template_replace['relative_path'] = \
                        template_replace['relative_path'][1:]

                    # replace specific template
                    for prop in template_all_props:
                        content = content.replace(
                            f'[template.{template.name}.{prop}]',
                            template_replace[prop]
                        )

                # save new content into the template
                self.configurable_file_repository.name = configurable.name
                self.configurable_file_repository.save(content)

                # save new content to the configurable in project
                # removing the template.All placeholders
                self.configurable_file_repository.path = \
                    self.configuration_repository.get_parent_path(
                        configurable.path)
                props = '|'.join(template_all_props)
                self.configurable_file_repository.save(
                    sub(f'(?<=\n).*\[template\.All\.({props})\].*\n',
                        lambda m: '',
                        content
                    )
                )


        self.configurable_file_repository.path = local_path
        self.configurable_file_repository.name = prev_name


class VariableService:
    '''Handle variable rules'''
    def __init__(self, repository, project_change_event):
        self.repository = repository
        project_change_event.subscribe(self.project_changed)

    def get(self):
        '''Get project variables'''
        return self.repository.get()

    @staticmethod
    def get_defaults():
        '''Returns default application variables'''
        return [Variable('ext', 'py')]

    def save_defaults(self):
        '''Saves default variables if them aren\'t deleted before
        and project is set
        '''
        if not self.repository.exists() and self.repository.path:
            for var in VariableService.get_defaults():
                self.add(var)

    def add(self, variable):
        '''Add variable'''
        if not self.repository.path:
            raise ProjectNotSet
        self.repository.add(variable)

    def change(self, old_name, variable):
        '''Updates variable'''
        variables = self.repository.get()
        db_variable = self.repository.first(lambda v: v.name == old_name,
                                            variables)
        if isinstance(db_variable, Variable):
            db_variable.name = variable.name
            db_variable.value = variable.value
            self.repository.save(variables)

    def remove(self, name):
        '''Removes variable by name'''
        self.repository.remove(lambda v: v.name == name)

    def project_changed(self, path):
        '''Project path change listener that change repository path when
        project path is changed
        '''
        self.repository.path = path
        self.save_defaults()


class FileService(ABC):
    '''Base service class for file model handlers'''
    def __init__(self, repository, file_repository):
        self.repository = repository
        self.file_repository = file_repository

    def create_child(self, parent, name):
        '''Add child node into the parent and get correct child path'''
        return self.repository.create_child(parent, name)

    def add(self, file_node, content):
        '''Add file node with content in the hard disk'''
        self.repository.add(file_node)
        self.file_repository.name = file_node.name
        self.file_repository.save(content)

    def save(self, file_node):
        '''Save file node state'''
        self.repository.update(file_node, file_node.name)

    def save_file(self, file_node, new_name, content):
        '''Write file node in the hard disk and rename if necessary'''
        if not new_name:
            new_name = file_node.name
        self.repository.update(file_node, new_name)
        self.file_repository.save_file(file_node.name, new_name, content)

    def remove(self, template):
        '''Removes file node from collection and its file'''
        self.repository.remove_node(template)
        self.file_repository.name = template.name
        self.file_repository.drop()


class TemplateService(FileService):
    '''Handle template rules'''
    def __init__(self, repository, file_repository, project_change_event):
        super().__init__(repository, file_repository)
        project_change_event.subscribe(self.project_changed)

    def get(self, template):
        '''Get file content'''
        self.file_repository.name = template.name
        return self.file_repository.get()

    def get_all(self):
        '''Get all templates'''
        return self.repository.get()

    def project_changed(self, path):
        '''Project path change listener that change repository path when
        project path is changed
        '''
        self.file_repository.path = path
        self.repository.path = path

    def get_path(self, template):
        '''Get template file path'''
        self.repository.name = template.name
        return OS.get_default_path(self.repository.full_path)


class ConfigurableService(FileService):
    '''Handle configurable rules'''
    def __init__(self, repository, file_repository, project_change_event):
        super().__init__(repository, file_repository)
        project_change_event.subscribe(self.project_changed)

    def get(self, configurable):
        '''Get file content'''
        previous_path = self.file_repository.path

        is_new = not self.repository.filter(
            lambda c: c.path == configurable.path
        )

        if is_new:
            self.file_repository.path = configurable.path
        else:
            self.file_repository.name = configurable.name

        content = self.file_repository.get()
        self.file_repository.path = previous_path
        return content

    def project_changed(self, path):
        '''Project path change listener that change repository path when
        project path is changed
        '''
        self.repository.path = path
        self.file_repository.path = path

    def get_filename(self, path):
        '''Get filename from entire path'''
        return self.repository.get_basename(path)

    def is_child(self, parent_path, filename):
        '''Verify if filename is a existent file into the parent_path folder'''
        return self.repository.is_child(parent_path, filename)
