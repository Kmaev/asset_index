import shutil
from pathlib import Path

from pxr import Usd, UsdGeom

from asset_index import config


class AssetEditor:
    def __init__(self, core, library):
        self.core_index = core
        self.library = library
        self.structure_config = config.FolderStructure()

        self.library_root = self.core_index.global_asset_lib
        self.library_path = self.core_index.global_asset_lib / library
        self.models_folder = self.library_path / self.structure_config.models_path

    def wrap_content(self, asset_path, root_folder):
        asset_path = Path(asset_path)
        wrapper = root_folder / asset_path.stem
        wrapper.mkdir(parents=True, exist_ok=True)
        shutil.move(str(asset_path), wrapper)

    def create_assets(self, usd_files: list):
        for file in usd_files:
            self.wrap_content(file, self.models_folder)

    def create_variant(self, stage_path, name, variant_dict):
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
