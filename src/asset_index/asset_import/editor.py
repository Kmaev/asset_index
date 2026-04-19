import shutil
from dataclasses import dataclass
from pathlib import Path

from asset_index import config


@dataclass
class EditResult:
    """Helper class to store editing result data after changing asset structure"""
    success: bool
    asset: Path | None = None


class AssetEditor:
    """
    Asset editor providing basic utilities to organise the library.
    Current features are minimal and intended to be extended.
    """

    def __init__(self, core, library):
        self.core_index = core
        self.library = library
        self.structure_config = config.FolderStructure()

        self.library_root = self.core_index.global_asset_lib
        self.library_path = self.core_index.global_asset_lib / library
        self.models_folder = self.library_path / self.structure_config.models_path

    def wrap_content(self, asset_path, root_folder) -> EditResult:
        """
        Wrap an asset into a folder named after the asset in case if the selected asset
        already has correct folder structure skips the asset and returns asset name
        """
        asset_path = Path(asset_path)
        wrapper = root_folder / asset_path.stem
        if wrapper.exists() or asset_path.parents[1] == self.models_folder:
            return EditResult(False, asset_path)
        wrapper.mkdir(parents=True, exist_ok=True)
        shutil.move(str(asset_path), wrapper)
        return EditResult(True, asset_path)

    def create_assets(self, usd_files: list) -> list[str]:
        """Wrap a list of USD files into the library structure. Returns skipped files as a list"""
        edit_results = [self.wrap_content(file, self.models_folder) for file in usd_files]
        errored_files = [result.asset.name for result in edit_results if not result.success]
        return errored_files
