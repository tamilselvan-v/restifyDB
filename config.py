import json


class ConfigReader:

    def __init__(self, filepath: str):
        """
        Read config
        """
        with open(filepath) as fp:
            self.config = json.load(fp)
