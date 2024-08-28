import argparse

import yaml
from easydict import EasyDict


class Configuration(EasyDict):
    def load(self, path):
        with open(path) as file:
            super().__init__(yaml.safe_load(file))


config = Configuration()


def load_config(path=None):
    if path is None:
        parser = argparse.ArgumentParser()
        parser.add_argument('--config')
        args = parser.parse_args()
        path = args.config
    config.load(path)
