from src.Configuration import Configuration

class App:
    def __init__(self):
        self.configuration = Configuration()

app = App()

import gui.init
