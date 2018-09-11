# -*- coding: utf-8 -*-
from gui.GuiHandler import GuiHandler

class App:
    def __init__(self):
        self.gui = GuiHandler()
        self.gui.start()

app = App()