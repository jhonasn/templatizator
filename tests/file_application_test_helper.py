from os.path import join, dirname, exists
from tests import project_path, create_test_project


class FileApplicationTestHelper:
    @staticmethod
    def test_create_child(application, file_nodes):
        for file_node in file_nodes:
            child = application.create_child(file_node, 'child')
            assert child.name == 'child'
            assert child.path == join(file_node.path, 'child')

    @staticmethod
    def test_save(application, file_nodes, get_all):
        for file_node in file_nodes:
            new_name = file_node.name + '_changed'
            file_node.name = new_name
            path = join(dirname(file_node.path), new_name)
            application.save(file_node)
            assert file_node.name == new_name
            assert file_node.path == path
            file_node = list(filter(lambda t: t.name == new_name, get_all()))
            assert any(file_node)
            file_node = file_node[0]
            assert file_node.name == new_name
            assert file_node.path == path

    @staticmethod
    def test_save_file(application, file_nodes, get_all):
        for file_node in file_nodes:
            new_name = file_node.name + '_changed'
            path = join(dirname(file_node.path), new_name)
            new_content = f'path: {path}'
            application.save_file(file_node, new_name, new_content)
            file_node = list(filter(lambda t: t.name == new_name, get_all()))
            assert any(file_node)
            file_node = file_node[0]
            assert file_node.name == new_name
            assert file_node.path == path
            content = application.get(file_node)
            assert content == new_content

    @staticmethod
    def test_remove(application, file_nodes, get_all):
        for file_node in file_nodes:
            assert any(filter(lambda t: t.name == file_node.name, get_all()))
            application.remove(file_node)
            assert not any(filter(lambda t: t.name == file_node.name, get_all()))

    @staticmethod
    def test_not_save_into_project(application, file_nodes, variables,
        save_into_project, get_directory=None):
        def variable_replace(text):
            for var in variables:
                text = text.replace(f'[{var.name}]', var.value)
            return text

        for file_node in file_nodes:
            file_node.save = False
            application.save(file_node)

            other_nodes = list(filter(
                lambda t: t is not file_node, file_nodes))

            for node in other_nodes:
                if not node.save:
                    node.save = True
                    application.save(node)

            from shutil import rmtree
            rmtree(project_path)
            save_into_project()

            #import pdb;pdb.set_trace(header=None)
            saved_name = variable_replace(file_node.name)
            path = None

            if get_directory:
                directory = get_directory(file_node)
                path = join(project_path, directory, saved_name)
            else:
                path = join(project_path, saved_name)

            assert not exists(path)
            for node in other_nodes:
                saved_name = variable_replace(node.name)
                if get_directory:
                    directory = get_directory(node)
                    path = join(project_path, directory, saved_name)
                else:
                    path = join(project_path, saved_name)
                assert exists(path)
