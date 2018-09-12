import os
import json

class Configuration:
    history_path = './history.json'
    # do que?
    history = []

    def __init__(self):
        #init history
        if os.path.exists(Configuration.history_path):
            Configuration.history = json.loads(open(Configuration.history_path).read())
        else:
            self.save_history()

        self.configuration_path = Configuration.history[0] if len(Configuration.history) > 0 else './'
        self.load()
        self.destination_path = self.destination_path if hasattr(self, 'destination_path') else os.path.expanduser("~")

    def get_configuration_json_path(self):
        return os.path.join(self.configuration_path, 'configuration.json')

    def load(self):
        if os.path.exists(self.get_configuration_json_path()):
            configuration = json.loads(open(self.get_configuration_json_path()))
            for key, value in configuration:
                self[key] = value

    def save_history(self):
        open(Configuration.history_path, 'w+').write(json.dumps(Configuration.history))

    def change_destination(self, path):
        self.path = path

    def add_variable(self, name, value):
        self.name = value

    def save(self):
        open(self.get_configuration_json_path , 'w+').write(json.dumps(self.__dict__))
