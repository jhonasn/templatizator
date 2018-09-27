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

