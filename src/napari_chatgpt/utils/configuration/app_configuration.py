import os
from threading import Lock
from typing import Union, Any

import yaml


class AppConfiguration:
    _instances = {}
    _lock = Lock()

    def __new__(cls, app_name, default_config="default_config.yaml"):
        """
        Implements a thread-safe singleton pattern for configuration instances per application name.
        
        Creates and returns a singleton instance of the configuration class for the specified application name. Ensures the application's configuration directory exists in the user's home directory.
        """
        with cls._lock:
            if app_name not in cls._instances:

                # Instantiate class:
                instance = super(AppConfiguration, cls).__new__(cls)

                # Save instance in class level dictionary:
                cls._instances[app_name] = instance

                # if folder doesn't exist, create it:
                if not os.path.exists(os.path.expanduser(f"~/.{app_name}")):
                    os.makedirs(os.path.expanduser(f"~/.{app_name}"), exist_ok=True)

            return cls._instances[app_name]

    def __init__(
        self, app_name, default_config: Union[str, dict] = "default_config.yaml"
    ):
        """
        Initialize the AppConfiguration instance with application name and default configuration.
        
        Parameters:
            app_name (str): The name of the application, used to determine the configuration directory.
            default_config (Union[str, dict], optional): Path to a default YAML config file or a dictionary of default settings. Defaults to "default_config.yaml".
        """
        self.app_name = app_name
        self.default_config = default_config
        self.config_file = os.path.expanduser(f"~/.{app_name}/config.yaml")
        self.config_data = {}
        self.load_configurations()

    def load_default_config(self):
        """
        Load and return the default configuration as a dictionary.
        
        If the default configuration is provided as a dictionary, it is returned directly. If it is a string, it is treated as a file path and the YAML file is loaded if it exists. Returns an empty dictionary if no valid default configuration is found.
        
        Returns:
            dict: The loaded default configuration, or an empty dictionary if unavailable.
        """
        if isinstance(self.default_config, dict):
            return self.default_config
        elif isinstance(self.default_config, str):
            default_config_path = os.path.abspath(self.default_config)
            if os.path.exists(default_config_path):
                with open(default_config_path, "r") as default_file:
                    return yaml.safe_load(default_file)
        return {}

    def load_configurations(self):
        # Load default configurations
        """
        Load and merge default and user-specific configuration data into the instance.
        
        Loads the default configuration, then overlays any user-specific settings from the configuration file if it exists. The resulting merged configuration is stored in `config_data`.
        """
        default_config = self.load_default_config()

        # Load user-specific configurations
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as user_file:
                user_config = yaml.safe_load(user_file)
        else:
            user_config = {}

        # Merge configurations
        self.config_data = {**default_config, **user_config}

    def save_configurations(self):
        """
        Persist the current configuration data to the configuration file in YAML format.
        """
        with open(self.config_file, "w") as file:
            yaml.dump(self.config_data, file)

    def get(self, key, default: Any = None):
        """
        Retrieve a configuration value for the given key, optionally setting and saving a default if the key is missing.
        
        Parameters:
            key: The configuration key to retrieve.
            default: The value to use and persist if the key is not present.
        
        Returns:
            The value associated with the key, or the provided default if the key was missing.
        """
        value = self.config_data.get(key)
        if value is None:
            value = default
            if value is not None:
                self.__setitem__(key, value)

        return value

    def __getitem__(self, key):
        return self.config_data.get(key)

    def __setitem__(self, key, value):
        """
        Set a configuration value for the given key and persist the change to disk.
        
        Parameters:
            key: The configuration key to set.
            value: The value to associate with the key.
        """
        self.config_data[key] = value
        self.save_configurations()
