from dataclasses import dataclass

from template_video_renderer.domain.video.value.scene_layer import SceneLayer


@dataclass(frozen=True)
class FramePlan:
    frame_index: int
    layers: tuple[SceneLayer, ...]

    @property
    def is_transition(self) -> bool:
        return len(self.layers) > 1
