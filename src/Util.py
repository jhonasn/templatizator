import os
import sys
import subprocess

class Util:
    def open_path_with_os(path):
        if sys.platform.find('win') > -1:
            os.startfile(path)
        elif sys.platform.find('linux') > -1:
            subprocess.check_call(['xdg-open', path])
        elif sys.platform.find('linux') > -1:
            subprocess.check_call(['open', path])

    def is_dark_theme():
        if os.path.exists('~/.config/gtk-3.0/settings.ini'):
            settings = open('~/.config/gtk-3.0/settings.ini').read()
            return settings.find('gtk-application-prefer-dark-theme=1')


