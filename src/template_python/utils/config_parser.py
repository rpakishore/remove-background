from pathlib import Path

import tomllib
from .logger import log
from functools import cached_property
from typing import Any


class Config:
    def __init__(self, filepath: Path | str) -> None:
        self.filepath: Path = Path(str(filepath))
        self.__env_overrides: dict[str, Any] = {}

        log.debug(f"{self.__str__()} Initialized.")

    def __str__(self) -> str:
        return f"Config(filepath={self.filepath})"

    def update_env(self, key: str, value: Any):
        """Allows key values to be overridden in exec.

        # Example usage
        ```python
        config = Config('path/to/config.toml')
        config.update_env(key='database' = {'host' = '127.0.0.1'})
        ```
        """
        self.__env_overrides[key] = value
        del self.value

    @cached_property
    def value(self) -> dict[str, Any]:
        """Get config value"""
        if self.filepath:
            try:
                with open(self.filepath, "r") as f:
                    return {**tomllib.loads(f.read()), **self.__env_overrides}
            except FileNotFoundError:
                log.warning(f"Config file not found in {self.filepath}")
            except Exception as e:
                log.error(msg=f"Error loading Config:\n{e}")
        return {**self.__env_overrides}

    def get(self, keys: tuple[str, ...], default=None):
        """Get the value from config"""
        data = self.value
        for key in keys[:-1]:
            data = data.get(key, {})
        return data.get(keys[-1], default)

    def exists(self) -> bool:
        """Check if config file exists"""

        if self.filepath is None or (not self.filepath.exists()):
            return False
        return True
