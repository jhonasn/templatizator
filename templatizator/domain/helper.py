'''Helpers for all application layers'''
import os
import sys
import subprocess


class OS:
    '''Helper to access or execute some operational system information'''
    is_linux = False
    is_windows = False
    is_mac = False

    is_bundled_project = False

    def __init__(self):
        raise Exception('Static class is not instantiable')

    @staticmethod
    def open_with(path):
        '''Open 'open with' dialog form operational system'''
        if OS.is_linux:
            subprocess.check_call(['xdg-open', path])
        elif OS.is_windows:
            os.startfile(path)
        elif OS.is_mac:
            subprocess.check_call(['open', path])

    @staticmethod
    def is_dark_theme():
        '''Returns True if the OS theme is dark.
        Currently it supports only gnome env.
        '''
        try:
            # GTK env
            process = subprocess.Popen(['gsettings', 'get',
                                        'org.gnome.desktop.interface',
                                        'gtk-theme'],
                                       stdout=subprocess.PIPE)
            res = str(process.communicate()[0])

            return res.find('dark') > -1
        # Necessary to start the application
        # pylint: disable=broad-except
        except Exception:
            return False

    @staticmethod
    def get_default_path(path):
        return os.path.normpath(path)

    @staticmethod
    def get_path(path):
        base = os.path.abspath(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        return os.path.normpath(os.path.join(base, path))


class Event:
    '''Help different classes to communicate with each other using instances
    of this class maintaining them decoupled
    '''
    def __init__(self):
        self.subscribers = []

    def subscribe(self, call_back):
        '''Subscribe to receive notifications of this event instance'''
        self.subscribers.append(call_back)

    def unsubscribe(self, call_back):
        '''Unsubscribe to stop receiving notifications of this event
        instance
        '''
        self.subscribers.remove(call_back)

    def publish(self, data):
        '''Notify subscribers of this event instance'''
        for call_back in self.subscribers:
            call_back(data)


if sys.platform.find('linux') > -1:
    OS.is_linux = True
elif sys.platform.find('win') > -1:
    OS.is_windows = True
elif sys.platform.find('darwin') > -1:
    OS.is_mac = True
