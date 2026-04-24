import logging
from pathlib import Path

from asset_index import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LibraryStructureResolver:
    """Class to validate folder and asset structure for a given library."""

    def __init__(self, core_index, library):
        """
        Initialize the resolver.

        Args:
            core_index: Library index providing access to asset libraries, metadata, and configuration.
            library: Asset library name.
        """
        self.core_index = core_index
        self.library_name = library
        self.structure_config = config.FolderStructure()

        self.library_path = self.core_index.global_asset_lib / library
        self.models_folder = self.library_path / self.structure_config.models_path

    def run_library_validation(self) -> tuple[bool, bool]:
        """
        Run folder and asset validation checks.

        Returns:
            tuple: Results of folder structure and asset structure validation.
        """
        folder_structure_check = self.validate_folder_structure()
        logger.info("Folder structure check: ", folder_structure_check)
        asset_structure_check = folder_structure_check and self.validate_asset_structure()
        logger.info("Asset check: ", asset_structure_check)
        return folder_structure_check, asset_structure_check

    def validate_folder_structure(self) -> bool:
        """
        Check required directory structure exists.

        Returns:
            bool: Result of folder structure validation.
        """
        return self.models_folder.is_dir()

    def validate_asset_structure(self) -> bool:
        """
        Check asset folder structure is correct and contains USD file.

        Returns:
            bool: Result of asset structure validation.
        """
        return any(asset.is_dir() and self._asset_has_valid_usd(asset)
                   for asset in self.models_folder.iterdir())

    @staticmethod
    def _asset_has_valid_usd(asset: Path) -> bool:
        """
        Check asset directory contains a matching USD file.

        Returns:
            bool: Whether the asset has a valid USD file.
        """
        return any(".usd" in f.suffix.lower() and asset.name.lower() in f.name.lower()
                   for f in asset.iterdir())
