import json


class Settings:
    def __init__(self, settings_file):
        # Load the settings from the file
        with open(settings_file, "r") as f:
            self.settings = json.load(f)

    def get_setting(self, setting_name):
        # Return the value of the requested setting
        return self.settings.get(setting_name, None)
