from dataclasses import dataclass

from template_video_renderer.domain.video.value.layout_spec import LayoutSpec
from template_video_renderer.domain.video.value.text_style import TextStyle


@dataclass(frozen=True)
class StyleSpec:
    title: TextStyle
    subtitle: TextStyle
    accent_color: str
    layout: LayoutSpec
