from dataclasses import dataclass

from template_video_renderer.domain.video.value.opacity import Opacity


@dataclass(frozen=True)
class SceneLayer:
    scene_index: int
    scene_opacity: Opacity
    title_opacity: Opacity
    subtitle_opacity: Opacity
    accent_progress: float
