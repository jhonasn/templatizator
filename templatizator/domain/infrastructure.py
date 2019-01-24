'''Infrastructure layer module'''


class ProjectNotSet(ResourceWarning):
    '''Warning raised when an action that depends on project path is triggered
    and the project path isn't set
    '''
    pass


class RepositoryPathNotSet(Exception):
    '''Warning raise when IO is triggered in a repository without path set'''
    pass
