import logging
from pathlib import Path

from asset_index import config
from asset_index.utils import import_utils

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LibraryStructureResolver:
    """Class to validate folder and asset structure for a given library."""

    def __init__(self, lib_name):
        self.lib_name = lib_name
        self.global_asset_lib = Path(import_utils.ImportUtils.get_env_var("GLOBAL_ASSET_LIB"))

        self.lib_path = self.global_asset_lib / lib_name
        if not self.lib_path.is_dir():
            raise FileNotFoundError("Library directory doesn't exists")

        self.structure_config = config.FolderStructure()

        self.models = self.lib_path / self.structure_config.models_path
        self.textures = self.lib_path / self.structure_config.textures_path

    def run_library_validation(self) -> tuple[bool, bool]:
        """Run folder and asset validation checks."""
        folder_structure_check = self.validate_folder_structure()
        logger.info("Folder structure check: ", folder_structure_check)
        asset_structure_check = folder_structure_check and self.validate_asset_structure()
        logger.info("Asset check: ", asset_structure_check)
        return folder_structure_check, asset_structure_check

    def validate_folder_structure(self) -> bool:
        """Check required directory structure exists."""
        required = (self.models, self.textures)
        return all(folder.is_dir() for folder in required)

    def validate_asset_structure(self) -> bool:
        """Check asset folder structure is correct and contains USD file."""
        return any(asset.is_dir() and self._asset_has_valid_usd(asset)
                   for asset in self.models.iterdir())

    @staticmethod
    def _asset_has_valid_usd(asset: Path) -> bool:
        """Check asset directory contains a matching USD file."""
        return any(".usd" in f.suffix.lower() and asset.name.lower() in f.name.lower()
                   for f in asset.iterdir())
