import os
from pathlib import Path
from typing import Any


class ImportUtils:
    """
    Static utilities for asset import workflows.
    """

    @staticmethod
    def get_env_var(env_var: str) -> str:
        try:
            return os.environ[env_var]
        except:
            raise EnvironmentError(f"Environment variable: '{env_var}' not found")

    @classmethod
    def path_to_str(cls, obj: Any) -> Any:
        """
        Recursively convert Path objects within a dictionary or list to strings.
        """
        if isinstance(obj, dict):
            return {str(k): cls.path_to_str(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [cls.path_to_str(i) for i in obj]
        elif isinstance(obj, Path):
            return str(obj)
        else:
            return obj
