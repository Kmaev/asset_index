import os


class ImportUtils:
    """Static utilities for asset import workflows."""

    @staticmethod
    def get_env_var(env_var: str) -> str:
        """Return the value of the given environment variable."""
        try:
            return os.environ[env_var]
        except KeyError:
            raise EnvironmentError(f"Environment variable '{env_var}' not found.")
