from dataclasses import dataclass

from template_video_renderer.domain.video.value.canvas_spec import CanvasSpec
from template_video_renderer.domain.video.value.encoding_spec import EncodingSpec
from template_video_renderer.domain.video.value.style_spec import StyleSpec
from template_video_renderer.domain.video.value.timing_spec import TimingSpec


@dataclass(frozen=True)
class AppSettings:
    environment: str
    ffmpeg_binary: str
    logging_level: str
    canvas: CanvasSpec
    style: StyleSpec
    timing: TimingSpec
    encoding: EncodingSpec
