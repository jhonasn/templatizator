from os.path import join, dirname


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
    def test_remove(application, templates, get_all):
        for template in templates:
            assert any(filter(lambda t: t.name == template.name, get_all()))
            application.remove(template)
            assert not any(filter(lambda t: t.name == template.name, get_all()))
