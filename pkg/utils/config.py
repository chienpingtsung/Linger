import argparse
from pathlib import Path
from typing import Optional, Union

import yaml
from easydict import EasyDict


class Config:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def load(self, path: Optional[Union[str, Path]] = None):
        config_path = Path(path or 'config/default.yaml')
        if not config_path.exists():
            raise FileNotFoundError(f'Config file not found at {config_path}')

        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = EasyDict(yaml.safe_load(f))

    def __getattr__(self, name):
        if self._config is None:
            raise RuntimeError('Config not init yet')
        return self._config[name]

    def __getitem__(self, name):
        return self.__getattr__(name)

    def get(self, key, default=None):
        try:
            return self.__getattr__(key)
        except KeyError:
            return default


cfg = Config()


def load_config(path=None):
    if path is None:
        parser = argparse.ArgumentParser()
        parser.add_argument('--config')
        args = parser.parse_args()
        path = args.config
    cfg.load(path)
