import shutil
from dataclasses import dataclass
from pathlib import Path

from pxr import Usd, UsdGeom

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

    @staticmethod
    def create_variant(stage_path, name, variant_dict):
        """Create a USD asset with variants from the given files."""
        stage = Usd.Stage.CreateNew(str(stage_path))

        root = UsdGeom.Xform.Define(stage, f"/{name}")
        root_prim = root.GetPrim()
        stage.SetDefaultPrim(root_prim)

        geo_path = root_prim.GetPath().AppendChild("geo")
        geo = stage.DefinePrim(geo_path, "Xform")

        variant_set = geo.GetVariantSets().AddVariantSet("model")

        for file_path, prim_path in variant_dict.items():
            variant_name = Path(file_path).stem

            variant_set.AddVariant(variant_name)
            variant_set.SetVariantSelection(variant_name)

            with variant_set.GetVariantEditContext():
                geo.GetReferences().ClearReferences()
                geo.GetReferences().AddReference(file_path, prim_path)

        if variant_dict:
            last_key = next(reversed(variant_dict))
            last_variant = Path(last_key).stem
            variant_set.SetVariantSelection(last_variant)

        stage.GetRootLayer().Save()

    def create_asset_with_variant(self, usd_files: list):
        """Create an asset and build a variant set from selected USD files."""
        user_selection = [Path(file) for file in usd_files]
        parent = user_selection[0].parent

        dest = self.models_folder / parent.name
        dest.mkdir(parents=True, exist_ok=True)
        shutil.move(str(parent), str(dest))

        stage_path = dest / f"{dest.name}.usda"
        name = dest.name
        _mod_user_selection = [Path(dest) / file.name for file in user_selection]

        variant_dict = {}

        for file in _mod_user_selection:
            variant_dict[str(file)] = f"/{file.stem}"

        self.create_variant(stage_path, name, variant_dict)
