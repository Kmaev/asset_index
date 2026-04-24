# Copyright (c) 2026 Kristina Maevskaya
# Asset Browser — portfolio project.
import shutil
from dataclasses import dataclass
from pathlib import Path

from asset_index import config
from asset_index.core.library_index import LibraryIndex


@dataclass
class EditResult:
    """
    Helper class to store editing result data after changing asset structure

    Args:
        success: Whether the asset was modified successfully.
        asset: Asset path associated with the operation.
    """
    success: bool
    asset: Path | None = None


class AssetEditor:
    """Asset editor providing basic utilities to organise the library."""

    def __init__(self, core: LibraryIndex, library: str):
        """
        Initialize the editor.

        Args:
            core: Library index providing access to asset libraries, metadata, and configuration.
            library: Asset library name for editing.
        """
        self.core_index = core
        self.library = library
        self.structure_config = config.FolderStructure()

        self.library_root = self.core_index.global_asset_lib
        self.library_path = self.core_index.global_asset_lib / library
        self.models_folder = self.library_path / self.structure_config.models_path

    def wrap_content(self, asset_path, root_folder) -> EditResult:
        """
        Wrap an asset into a folder named after the asset.

        If the asset already has the correct folder structure, it is skipped.

        Args:
            asset_path: Source USD file path.
            root_folder: Library models root folder where the asset will be moved.

        Returns:
            EditResult: Result indicating whether the asset was modified and the input asset path.
        """
        asset_path = Path(asset_path)
        wrapper = root_folder / asset_path.stem
        if wrapper.exists() or asset_path.parents[1] == self.models_folder:
            return EditResult(False, asset_path)
        wrapper.mkdir(parents=True, exist_ok=True)
        shutil.move(str(asset_path), wrapper)
        return EditResult(True, asset_path)

    def create_assets(self, usd_files: list) -> list[str]:
        """
        Wrap a list of USD files into the library structure.

        Args:
            usd_files: List of USD file to process.

        Returns:
            List of skipped files.
        """
        edit_results = [self.wrap_content(file, self.models_folder) for file in usd_files]
        errored_files = [result.asset.name for result in edit_results if not result.success]
        return errored_files
