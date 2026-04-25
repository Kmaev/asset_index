from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FolderStructure:
    """
    Defines the expected folder structure for assets.

    In this example, assets are organized into two folders: Models and Textures.
    Each asset in the Models folder is expected to be contained in its own directory,
    with the directory name matching the name of the corresponding USD file.
    """
    models_path: str = "Models"


@dataclass
class CameraSettings:
    """Camera parameters used for thumbnail rendering."""
    focal_length: float = 50.0
    sensor_width: float = 36.0
    azimuth: float = 45
    elevation: float = 20
    distance: float = 1.3


@dataclass
class LightingSettings:
    """Lighting configuration for thumbnail rendering."""
    hdr: Path = Path(__file__).resolve().parents[2] / "resources" / "belfast_farmhouse_2k.hdr"
    intensity: float = 0.85
    # Final exposure is adjusted based on asset scale.
    # For very small assets, intensity can be reduced to avoid overexposure.
    # For large assets, intensity scaling is limited by `exposure_clamp` to prevent overly bright lighting.
    exposure: float = 0.6
    exposure_clamp: float = 1.2


@dataclass
class ImageSettings:
    """
    Settings for rendering via `usdrecord`.
    Field values must match the expected `usdrecord` command-line parameters.
    """
    image_width: str = "140"
    color_correction: str = "disabled"
    renderer: str = "Storm"
    complexity: str = "veryhigh"
    extension: str = ".png"


@dataclass
class RenderConfig:
    """Container for render configuration settings."""
    lighting: LightingSettings = field(default_factory=LightingSettings)
    camera: CameraSettings = field(default_factory=CameraSettings)
    image: ImageSettings = field(default_factory=ImageSettings)
