import os
import sys
import subprocess

class OS:
    is_linux = False
    is_windows = False
    is_mac = False

    def open_with(path):
        if is_linux:
            subprocess.check_call(['xdg-open', path])
        elif is_windows:
            os.startfile(path)
        elif is_mac:
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

if sys.platform.find('linux') > -1:
    OS.is_linux = True
elif sys.platform.find('win') > -1:
    OS.is_windows = True
elif sys.platform.find('darwin') > -1:
    OS.is_mac = True

