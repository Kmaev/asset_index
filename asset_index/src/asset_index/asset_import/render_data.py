from dataclasses import dataclass

@dataclass
class RenderConfig:
    camera_sensor: float
    camera_focal_length: float
    distance_to_object: float
    camera_rotation: float
    camera_elevation: float
    light_intensity_clamping: float
    object_size_threshold: float