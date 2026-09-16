from typing import Protocol

from template_video_renderer.domain.video.entity.video_project import VideoProject
from template_video_renderer.domain.video.value.canvas_spec import CanvasSpec
from template_video_renderer.domain.video.value.frame_image import FrameImage
from template_video_renderer.domain.video.value.frame_plan import FramePlan
from template_video_renderer.domain.video.value.style_spec import StyleSpec


class FrameRenderer(Protocol):
    def render(
        self,
        project: VideoProject,
        plan: FramePlan,
        canvas: CanvasSpec,
        style: StyleSpec,
    ) -> FrameImage: ...
