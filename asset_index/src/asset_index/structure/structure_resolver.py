import json
import logging
from pathlib import Path

from asset_index.utils import import_utils

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LibraryStructureResolver:
    def __init__(self, lib_name):
        self.lib_name = lib_name
        self.global_asset_lib = Path(import_utils.ImportUtils.get_env_var("GLOBAL_ASSET_LIB"))

        self.lib_path = self.global_asset_lib / lib_name
        if not self.lib_path.is_dir():
            raise FileNotFoundError("Library directory doesn't exists")
        current_dir = Path(__file__).parent
        structure_config = current_dir / "structure_config.json"
        with open(structure_config, "r") as f:
            config = json.load(f)
        self.models = self.lib_path / config["models_path"]
        self.textures = self.lib_path / config["textures_path"]
        self.material = self.lib_path / config["materials_path"]

    def run_library_validation(self) -> tuple[bool, bool]:
        folder_structure_check = self.validate_folder_structure()
        logger.info("Folder structure check: ", folder_structure_check)
        asset_structure_check = folder_structure_check and self.validate_asset_structure()
        logger.info("Asset check: ", asset_structure_check)
        return folder_structure_check, asset_structure_check

    def validate_folder_structure(self) -> bool:
        required = (self.models, self.textures, self.material)
        return all(folder.is_dir() for folder in required)

    def validate_asset_structure(self) -> bool:
        return any(asset.is_dir() and self._asset_has_valid_usd(asset)
                   for asset in self.models.iterdir())

    def _asset_has_valid_usd(self, asset: Path) -> bool:
        return any(f.suffix.lower() == ".usd" and asset.name.lower() in f.name.lower()
                   for f in asset.iterdir())
