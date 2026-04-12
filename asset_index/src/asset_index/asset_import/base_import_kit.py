import json
import logging
import math
import subprocess
import tempfile
from collections import defaultdict
from collections.abc import Iterator
from pathlib import Path

from pxr import Usd, UsdGeom, UsdLux, Sdf, Gf

from asset_index.utils import import_utils

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BaseKitImporter:
    """
    Base class for importing KitBash asset libraries into a production pipeline.
    For each USD asset, creates a temporary render file, computes the asset’s bounding box, and uses it to set up and position a render camera. Adds a basic light rig and generates a thumbnail using usdrecord with the Storm renderer.
    Updates the global library metadata file with the library key and asset paths
    """

    def __init__(self, library_path: str):
        self.global_asset_lib = Path(import_utils.ImportUtils.get_env_var("GLOBAL_ASSET_LIB"))

        self.library_path = Path(library_path)
        self.global_asset_catalog = self.library_path / "library_catalog.json"

        self.models_folder = self.library_path / "Models"
        self.added_new_assets = False

    def import_library(self) -> None:
        """
        Run the full import: build the library catalog, render thumbnails, and update global metadata.
        """
        library_catalog = self.create_library_catalog()

        library_name = self.library_path.name
        assets = library_catalog[library_name]
        self.render_thumbnails(assets)
        if self.added_new_assets:
            self.update_global_library_index(library_catalog)

    def create_library_catalog(self) -> dict[str, list[Path]]:
        """
        Map library path to a list of USD asset files.
        """
        library_catalog = defaultdict(list)
        library_name = self.library_path.name
        if self.models_folder.is_dir():
            for asset_folder in self.models_folder.iterdir():
                if asset_folder.is_dir():
                    for file in asset_folder.iterdir():
                        if asset_folder.name in file.name and "usd" in file.suffix:
                            library_catalog[library_name].append(file)
        return library_catalog

    def render_thumbnails(self, assets: list[Path]) -> None:
        """
        Render thumbnails for USD assets by creating a temporary stage and calling the renderer.
        """
        for asset_path in self.iterate_with_progress_bar(assets):
            thumbnail_file = self.get_thumbnail_output_path(asset_path, "png")
            if Path(thumbnail_file).exists():
                logger.info(f"Thumbnail exists: {str(thumbnail_file)}")
                continue
            temp_usd_file = self.create_temp_usd_render_stage(asset_path)
            self.render_usd_stage(str(temp_usd_file), str(thumbnail_file))
            self.added_new_assets = True

    def iterate_with_progress_bar(self, assets: list[Path]) -> Iterator[Path]:
        """
        Iterate over assets while reporting render progress.
        Default implementation logs progress; may be overridden for DCC-specific behavior.
        """
        for asset in assets:
            logging.info(f"Generating thumbnail: {asset}")
            yield asset

    def update_global_library_index(self, library_catalog: dict[str, list[Path]]):
        """
        Sync a library catalog into the global metadata file.
        """
        if self.global_asset_catalog.exists():
            with open(self.global_asset_catalog, "r") as f:
                library_data = json.load(f)

        else:
            library_data = {}

        _converted_lib = import_utils.ImportUtils.path_to_str(library_catalog)
        for key, val in _converted_lib.items():
            if key in library_data:
                _library_data_set = set(library_data[key])
                _library_data_set.update(val)
                library_data[key] = sorted(list(_library_data_set))
            else:
                library_data[key] = sorted(val)

        with open(self.global_asset_catalog, "w") as f:
            json.dump(library_data, f, indent=4, default=str)

    @staticmethod
    def get_thumbnail_output_path(usd_file_path: Path, ext: str) -> Path:
        """
        Generate the thumbnail path by replacing the USD file extension with the specified extension.
        """
        return usd_file_path.with_suffix(f".{ext}")

    def create_temp_usd_render_stage(self, usd_file_path: Path) -> Path:
        """
        Create a temporary USD stage, reference the asset at the "/main" prim,
        attach a light rig and camera, and save for rendering.
        """
        asset_name = usd_file_path.stem
        asset_prim_path = Sdf.Path(f"/main/{asset_name}")

        tmp_dir_usd = Path(tempfile.gettempdir())
        temp_usd_stage_file = tmp_dir_usd / f"{asset_name}.usda"

        stage = Usd.Stage.CreateNew(str(temp_usd_stage_file))

        self.reference_library_asset(str(usd_file_path), stage, asset_prim_path)
        self.add_light_rig(stage)
        self.add_render_camera(stage)

        stage.Save()
        return temp_usd_stage_file

    @staticmethod
    def reference_library_asset(usd_file_path: str, stage: Usd.Stage, asset_prim_path: Sdf.Path):
        """
        Reference the asset at the specified prim path.
        """
        parent_prim = stage.DefinePrim(asset_prim_path)
        stage.SetDefaultPrim(parent_prim)
        references = parent_prim.GetReferences()
        references.AddReference(usd_file_path)

    @staticmethod
    def add_light_rig(stage: Usd.Stage):
        """
        Add a basic light rig with a Dome Light.
        """
        dome = UsdLux.DomeLight.Define(stage, "/DomeLight")
        dome.CreateIntensityAttr(100.0)

    @staticmethod
    def add_render_camera(stage: Usd.Stage):
        """
        Compute asset's bounding box and based on size calculate render camera position and rotation.
        Set up camera parameters.
        """
        camera = UsdGeom.Camera.Define(stage, "/Camera")

        prim = stage.GetPrimAtPath("/main")
        bbox_cache = UsdGeom.BBoxCache(
            Usd.TimeCode.Default(),
            [UsdGeom.Tokens.default_]
        )

        bbox = bbox_cache.ComputeWorldBound(prim)
        bbox_range = bbox.GetRange()

        center = bbox_range.GetMidpoint()
        size = bbox_range.GetSize()
        max_dim = max(size)

        sensor_width = 36.0
        focal_length = 50.0

        field_of_view = 2 * math.atan(sensor_width / (2 * focal_length))
        distance = (max_dim / 2) / math.tan(field_of_view / 2)
        distance *= 1.3

        azimuth = math.radians(45.0)
        elevation = math.radians(20.0)

        x = math.cos(elevation) * math.cos(azimuth)
        y = math.sin(elevation)
        z = math.cos(elevation) * math.sin(azimuth)

        offset = Gf.Vec3d(x, y, z)

        camera_position = center + offset * distance

        transform = Gf.Matrix4d()
        transform.SetLookAt(camera_position, center, Gf.Vec3d(0, 1, 0))
        rot = transform.ExtractRotation()
        camera_rotate = rot.Decompose(Gf.Vec3d(1, 0, 0),
                                      Gf.Vec3d(0, 1, 0),
                                      Gf.Vec3d(0, 0, 1))
        camera_rotate *= -1

        camera.AddTranslateOp().Set(camera_position)
        camera.AddRotateXYZOp().Set(camera_rotate)
        camera.CreateClippingRangeAttr().Set(Gf.Vec2f(0.001, 10000.0))
        camera.CreateFocalLengthAttr().Set(focal_length)
        camera.CreateHorizontalApertureAttr().Set(sensor_width)
        camera.CreateVerticalApertureAttr().Set(sensor_width)

    @staticmethod
    def render_usd_stage(usd_file: str, output_img_path: str, remove_usd_file: bool = True):
        """
        Execute render using usdrecord and the Storm renderer. Remove the temporary USD file.
        """
        cmd = [
            "usdrecord",
            usd_file,
            output_img_path,
            "--complexity", "veryhigh",
            "--colorCorrectionMode", "sRGB",
            "--renderer", "Storm",
            "--camera", "/Camera",
            "--imageWidth", "180"
        ]
        try:
            subprocess.run(cmd, check=True)
        finally:
            if remove_usd_file:
                Path(usd_file).unlink(missing_ok=True)
