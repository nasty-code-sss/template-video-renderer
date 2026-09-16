from dataclasses import dataclass

from template_video_renderer.domain.video.entity.video_project import VideoProject


@dataclass(frozen=True)
class RenderVideoInput:
    project: VideoProject
    destination: str
