import os
import yaml
from typing import Optional, Dict, Any


class Config:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'config.yaml'
            )
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def reload(self):
        self.config = self._load_config()

    @property
    def ocr(self) -> Dict[str, Any]:
        return self.config.get('ocr', {})

    @property
    def click(self) -> Dict[str, Any]:
        return self.config.get('click', {})

    @property
    def task(self) -> Dict[str, Any]:
        return self.config.get('task', {})

    @property
    def quantity(self) -> Dict[str, Any]:
        return self.config.get('quantity', {})

    @property
    def logging(self) -> Dict[str, Any]:
        return self.config.get('logging', {})

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)
