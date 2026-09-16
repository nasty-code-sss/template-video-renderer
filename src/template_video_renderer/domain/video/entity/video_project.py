from dataclasses import dataclass

from template_video_renderer.domain.video.entity.scene import Scene
from template_video_renderer.domain.video.error.empty_project_error import EmptyProjectError


@dataclass(frozen=True)
class VideoProject:
    name: str
    scenes: tuple[Scene, ...]
    audio_reference: str | None

    def __post_init__(self) -> None:
        if not self.scenes:
            raise EmptyProjectError(f"project '{self.name}' has no scenes to render")

    @property
    def scene_count(self) -> int:
        return len(self.scenes)

    @property
    def has_audio(self) -> bool:
        return self.audio_reference is not None

    def scene_at(self, index: int) -> Scene:
        return self.scenes[index]
