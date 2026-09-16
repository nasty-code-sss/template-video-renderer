from dataclasses import dataclass

from template_video_renderer.domain.video.value.frame_rate import FrameRate
from template_video_renderer.domain.video.value.resolution import Resolution


@dataclass(frozen=True)
class CanvasSpec:
    resolution: Resolution
    frame_rate: FrameRate
    background_color: str
