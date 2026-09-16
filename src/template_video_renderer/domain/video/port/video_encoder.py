from collections.abc import Iterable
from typing import Protocol

from template_video_renderer.domain.video.value.canvas_spec import CanvasSpec
from template_video_renderer.domain.video.value.encoding_spec import EncodingSpec
from template_video_renderer.domain.video.value.frame_image import FrameImage


class VideoEncoder(Protocol):
    def encode(
        self,
        frames: Iterable[FrameImage],
        canvas: CanvasSpec,
        spec: EncodingSpec,
        destination: str,
        audio_reference: str | None,
    ) -> None: ...
