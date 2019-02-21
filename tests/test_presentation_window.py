from templatizator.presentation.container import Container
from tests import container

namespace = 'templatizator.presentation.window'


def test_initialization(container):
    win = Container.window
    assert bool(win.application)
    assert bool(win.template_application)
    assert bool(win.configurable_application)
    assert bool(win.variables)
    assert bool(win.editor)
    assert bool(win.window)
    assert bool(win.treeview)

def test_icons(container, monkeypatch):
    '''test methods get_filetree_icon, get_filetree_action_icon
    and get_filetree_checkbox'''
    from templatizator.presentation.window import ICONS, ICONS_UGLY, ICON_ADD,\
        ICON_REMOVE, ICON_CHECKED, ICON_UNCHECKED
    from templatizator.domain.domain import Directory, Template, \
        ConfigurableFile
    win = Container.window
    # do not use helper to convert unicode icon
    monkeypatch.setattr(f'{namespace}.get_tkinter_unicode', lambda i: i)

    win.pretty_icons = True
    node = Directory(opened=True)
    assert node.open == True
    icon = win.get_filetree_icon(node)
    assert icon == ICONS.folderopened
    win.pretty_icons = False
    icon = win.get_filetree_icon(node)
    assert icon == ICONS_UGLY.folderopened
    assert icon != ICONS.folderopened
    icon = win.get_filetree_action_icon(node)
    assert icon == ICON_ADD
    icon = win.get_filetree_checkbox(node)
    assert icon == ''

    win.pretty_icons = True
    node = Directory(opened=False)
    assert node.open == False
    icon = win.get_filetree_icon(node)
    assert icon == ICONS.folderclosed
    win.pretty_icons = False
    icon = win.get_filetree_icon(node)
    assert icon == ICONS_UGLY.folderclosed
    assert icon != ICONS.folderclosed
    icon = win.get_filetree_action_icon(node)
    assert icon == ICON_ADD
    icon = win.get_filetree_checkbox(node)
    assert icon == ''

    win.pretty_icons = True
    node = Template(save=True)
    assert node.save == True
    icon = win.get_filetree_icon(node)
    assert icon == ICONS.template
    win.pretty_icons = False
    icon = win.get_filetree_icon(node)
    assert icon == ICONS_UGLY.template
    assert icon != ICONS.template
    icon = win.get_filetree_action_icon(node)
    assert icon == ICON_REMOVE
    icon = win.get_filetree_checkbox(node)
    assert icon == ICON_CHECKED
    node = Template(save=False)
    assert node.save == False
    icon = win.get_filetree_checkbox(node)
    assert icon == ICON_UNCHECKED
    assert icon != ICON_CHECKED

    win.pretty_icons = True
    node = ConfigurableFile(save=True)
    assert node.save == True
    icon = win.get_filetree_icon(node)
    assert icon == ICONS.configurable
    win.pretty_icons = False
    icon = win.get_filetree_icon(node)
    assert icon == ICONS_UGLY.configurable
    assert icon != ICONS.configurable
    icon = win.get_filetree_action_icon(node)
    assert icon == ICON_REMOVE
    icon = win.get_filetree_checkbox(node)
    assert icon == ICON_CHECKED
    node = ConfigurableFile(save=False)
    assert node.save == False
    icon = win.get_filetree_checkbox(node)
    assert icon == ICON_UNCHECKED
    assert icon != ICON_CHECKED

#def test_render_treeview(container):
#def test_fill_treeview(container):
#def test_select_project(container):
#def test_project_selected(container):
#def test_select_configuration(container):
#def test_configuration_selected(container):
#def test_add_template(container):
#def test_add_configurable(container):
#def test_open_file(container):
#def test_open_with(container):
#def test_remove_file(container):
#def test_row_popup_selected(container):
#def test_row_selected(container):
#def test_row_opened(container):
#def test_row_closed(container):
#def test_before_show_tooltip(container):
#def test_save_templates(container):
#def test_center(container):
