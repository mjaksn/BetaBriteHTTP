import json
import os


class ConfigurationProvider:

    def __init__(self, config_file_name: str = "config.json"):
        cwd = os.path.dirname(os.path.realpath(__file__))
        self._config_file_name = f"{cwd}/{config_file_name}"
        self._parse_config_file()

    @property
    def com_port(self) -> str:
        return self._com_port

    def _parse_config_file(self):
        config_file = open(self._config_file_name)
        config_data = json.load(config_file)
        self._com_port: str = config_data['com_port']
