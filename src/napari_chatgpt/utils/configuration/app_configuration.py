import os
from threading import Lock
from typing import Union, Any

import yaml


class AppConfiguration:
    _instances = {}
    _lock = Lock()

    def __new__(cls, app_name, default_config='default_config.yaml'):
        with cls._lock:
            if app_name not in cls._instances:

                # Instantiate class:
                instance = super(AppConfiguration, cls).__new__(cls)

                # Save instance in class level dictionary:
                cls._instances[app_name] = instance

                # if folder doesn't exist, create it:
                if not os.path.exists(os.path.expanduser(f'~/.{app_name}')):
                    os.makedirs(os.path.expanduser(f'~/.{app_name}'), exist_ok=True)

            return cls._instances[app_name]

    def __init__(self, app_name, default_config: Union[str, dict]='default_config.yaml'):
        self.app_name = app_name
        self.default_config = default_config
        self.config_file = os.path.expanduser(f'~/.{app_name}/config.yaml')
        self.config_data = {}
        self.load_configurations()

    def load_default_config(self):
        if isinstance(self.default_config, dict):
            return self.default_config
        elif isinstance(self.default_config, str):
            default_config_path = os.path.abspath(self.default_config)
            if os.path.exists(default_config_path):
                with open(default_config_path, 'r') as default_file:
                    return yaml.safe_load(default_file)
        return {}

    def load_configurations(self):
        # Load default configurations
        default_config = self.load_default_config()

        # Load user-specific configurations
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as user_file:
                user_config = yaml.safe_load(user_file)
        else:
            user_config = {}

        # Merge configurations
        self.config_data = {**default_config, **user_config}

    def save_configurations(self):
        with open(self.config_file, 'w') as file:
            yaml.dump(self.config_data, file)

    def get(self, key, default: Any = None):
        value = self.config_data.get(key)
        if value is None:
            value = default
            if value is not None:
                self.__setitem__(key, value)

        return value

    def __getitem__(self, key):
        return self.config_data.get(key)

    def __setitem__(self, key, value):
        self.config_data[key] = value
        self.save_configurations()

