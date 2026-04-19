import json
import logging
import math
import subprocess
import tempfile
from collections.abc import Iterator
from dataclasses import dataclass, asdict, field
from pathlib import Path

from pxr import Usd, UsdGeom, UsdLux, Sdf, Gf

from asset_index import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class LibraryData:
    """Container for library asset data."""
    assets: list = field(default_factory=list)
    extension: str = ".png"


class BaseKitImporter:
    """
    Base class for importing asset libraries into a production pipeline.
    For each USD asset, creates a temporary render file, computes the asset’s bounding box,
    and uses it to set up and position a render camera. Adds a basic light rig
    and generates a thumbnail using usdrecord.
    Updates the library metadata file.
    """

    def __init__(self, core_index, library: str):
        self.core_index = core_index
        self.library_name = library

        self.render_config = config.RenderConfig()
        self.folder_config = config.FolderStructure()

        self.all_libraries_data_file = self.core_index.all_libraries_data_file
        self.all_imported_libraries = self.core_index.list_imported_libraries()

        self.library_path = self.core_index.global_asset_lib / library
        self.models_folder = self.library_path / self.folder_config.models_path

        self.library_catalog = self.core_index.load_library_catalog(self.library_name)
        self.existing_library_data = self.map_existing_library_catalog(self.library_catalog)

        self.added_new_assets = False
        self.completed = False
        self.interrupted = False

    @staticmethod
    def map_existing_library_catalog(library_catalog: dict | None) -> LibraryData:
        """Map JSON library catalog data to a LibraryData instance."""
        if library_catalog:
            existing_library_data = LibraryData(**library_catalog)
            if existing_library_data.assets:
                existing_library_data.assets = [Path(asset) for asset in existing_library_data.assets]
            return existing_library_data
        else:
            return LibraryData()

    def import_library(self) -> None:
        """Run the full import: build the library catalog, render thumbnails, and update global metadata."""
        library_catalog = self.create_library_catalog()

        self.render_thumbnails(library_catalog.assets)

        if self.completed and self.added_new_assets:
            _converted_lib = asdict(library_catalog)
            _converted_lib["assets"] = [str(p) for p in _converted_lib["assets"]]

            self.update_library_index(_converted_lib)
            self.update_imported_libraries_index(self.library_name)

    def create_library_catalog(self) -> LibraryData:
        """Collect USD asset files from the models_folder directory and return them as a LibraryData instance."""
        _assets = []
        if self.models_folder.is_dir():
            for asset_folder in self.models_folder.iterdir():
                if asset_folder.is_dir():
                    for file in asset_folder.iterdir():
                        if asset_folder.name in file.name and "usd" in file.suffix:
                            _assets.append(file)
        _assets = sorted(_assets)
        return LibraryData(assets=_assets, extension=self.render_config.image.extension)

    def render_thumbnails(self, assets: list[Path]) -> None:
        """Render thumbnails for USD assets by creating a temporary stage."""
        self.completed = False
        self.interrupted = False
        processed = 0

        for asset_path in self.iterate_with_progress_bar(assets):
            thumbnail_file = self.get_thumbnail_output_path(asset_path, self.render_config.image.extension)
            if thumbnail_file.exists() and asset_path in self.existing_library_data.assets:
                processed += 1
                logger.info(f"Thumbnail exists: {str(thumbnail_file)}")
                continue

            temp_usd_file = self.create_temp_usd_render_stage(asset_path)
            try:
                self.render_usd_stage(str(temp_usd_file), str(thumbnail_file))
                processed += 1
                self.added_new_assets = True
            except Exception:
                thumbnail_file.unlink(missing_ok=True)
                raise
            if self.interrupted:
                thumbnail_file.unlink(missing_ok=True)
                break
        self.completed = (processed == len(assets))

    def iterate_with_progress_bar(self, assets: list[Path]) -> Iterator[Path]:
        """
        Report render progress.
        Default implementation logs progress, may be overridden for DCC-specific behavior.
        """
        for asset in assets:
            logging.info(f"Generating thumbnail: {asset}")

            yield asset

    @staticmethod
    def get_thumbnail_output_path(usd_file_path: Path, ext: str) -> Path:
        """Generate the thumbnail path by replacing the USD file extension with the specified extension."""
        return usd_file_path.with_suffix(ext)

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
        """Reference the asset at the specified prim path."""
        parent_prim = stage.DefinePrim(asset_prim_path)
        stage.SetDefaultPrim(parent_prim)
        references = parent_prim.GetReferences()
        references.AddReference(usd_file_path)

    @staticmethod
    def calculate_bbox_data(stage: Usd.Stage, prim_path: str):
        """Calculate the bounding box center, size, and maximum dimension for a given primitive."""
        prim = stage.GetPrimAtPath(prim_path)
        bbox_cache = UsdGeom.BBoxCache(
            Usd.TimeCode.Default(),
            [UsdGeom.Tokens.default_]
        )

        bbox = bbox_cache.ComputeWorldBound(prim)
        bbox_range = bbox.GetRange()

        center = bbox_range.GetMidpoint()
        size = bbox_range.GetSize()
        max_dim = max(size)
        return center, size, max_dim

    def add_light_rig(self, stage: Usd.Stage):
        """Add a basic light rig with a Dome Light."""
        _, size, max_dim = self.calculate_bbox_data(stage, "/main")
        exposure = self.render_config.lighting.exposure
        intensity = self.render_config.lighting.intensity
        exposure_clamp = self.render_config.lighting.exposure_clamp
        exposure *= max_dim if max_dim < exposure_clamp else exposure_clamp

        hdr = self.render_config.lighting.hdr
        dome = UsdLux.DomeLight.Define(stage, "/DomeLight")

        dome.CreateTextureFileAttr().Set(str(hdr))
        dome.CreateIntensityAttr().Set(intensity)
        dome.CreateExposureAttr().Set(exposure)

    def add_render_camera(self, stage: Usd.Stage):
        """
        Create render camera and based on bounding box data calculate render camera position and rotation.
        Set up camera parameters.
        """
        camera = UsdGeom.Camera.Define(stage, "/Camera")

        center, size, max_dim = self.calculate_bbox_data(stage, "/main")

        sensor_width = self.render_config.camera.sensor_width
        focal_length = self.render_config.camera.focal_length

        field_of_view = 2 * math.atan(sensor_width / (2 * focal_length))
        distance = (max_dim / 2) / math.tan(field_of_view / 2)
        distance *= self.render_config.camera.distance

        azimuth = math.radians(self.render_config.camera.azimuth)
        elevation = math.radians(self.render_config.camera.elevation)

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

    def render_usd_stage(self, usd_file: str, output_img_path: str, remove_usd_file: bool = True):
        """Execute render using usdrecord and the Storm renderer. Remove the temporary USD file."""
        cmd = [
            "usdrecord",
            usd_file,
            output_img_path,
            "--complexity", self.render_config.image.complexity,
            "--colorCorrectionMode", self.render_config.image.color_correction,
            "--renderer", self.render_config.image.renderer,
            "--camera", "/Camera",
            "--imageWidth", self.render_config.image.image_width
        ]
        try:
            subprocess.run(cmd, check=True)
        finally:
            if remove_usd_file:
                Path(usd_file).unlink(missing_ok=True)

    def update_library_index(self, library_catalog: dict):
        """Update library data catalog"""
        library_catalog_file_path = self.library_path / self.core_index.library_catalog_file_name
        with open(library_catalog_file_path, "w") as f:
            json.dump(library_catalog, f, indent=4)

    def update_imported_libraries_index(self, library: str) -> None:
        """Add a library into an imported library metadata file."""
        if library not in self.all_imported_libraries:
            self.all_imported_libraries.append(library)

        imported_libraries = sorted(self.all_imported_libraries)
        with open(self.core_index.all_libraries_data_file, "w") as f:
            json.dump(imported_libraries, f, indent=4, default=str)
