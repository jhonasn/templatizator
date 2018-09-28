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
        try:
            #GTK
            process = subprocess.Popen(['gsettings', 'get',
                'org.gnome.desktop.interface', 'gtk-theme'],
                stdout=subprocess.PIPE
            )
            res = str(process.communicate()[0])

            return res.find('dark') > -1
        except Exception:
            pass

        return False

