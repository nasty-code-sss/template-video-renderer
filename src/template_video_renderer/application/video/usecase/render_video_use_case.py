from collections.abc import Iterator

from template_video_renderer.application.video.dto.render_video_input import RenderVideoInput
from template_video_renderer.application.video.dto.render_video_output import RenderVideoOutput
from template_video_renderer.application.video.port.progress_reporter import ProgressReporter
from template_video_renderer.domain.video.entity.video_project import VideoProject
from template_video_renderer.domain.video.policy.scene_timeline import SceneTimeline
from template_video_renderer.domain.video.port.frame_renderer import FrameRenderer
from template_video_renderer.domain.video.port.video_encoder import VideoEncoder
from template_video_renderer.domain.video.value.canvas_spec import CanvasSpec
from template_video_renderer.domain.video.value.encoding_spec import EncodingSpec
from template_video_renderer.domain.video.value.frame_image import FrameImage
from template_video_renderer.domain.video.value.style_spec import StyleSpec
from template_video_renderer.domain.video.value.timing_spec import TimingSpec


class RenderVideoUseCase:
    def __init__(
        self,
        frame_renderer: FrameRenderer,
        video_encoder: VideoEncoder,
        canvas: CanvasSpec,
        style: StyleSpec,
        timing: TimingSpec,
        encoding: EncodingSpec,
        progress: ProgressReporter,
    ) -> None:
        self._frame_renderer = frame_renderer
        self._video_encoder = video_encoder
        self._canvas = canvas
        self._style = style
        self._timing = timing
        self._encoding = encoding
        self._progress = progress

    def execute(self, request: RenderVideoInput) -> RenderVideoOutput:
        timeline = SceneTimeline(request.project, self._timing, self._canvas.frame_rate)
        total_frames = timeline.total_frames
        self._progress.frames_planned(total_frames, timeline.total_seconds)

        self._progress.encoding_started(request.destination)
        self._video_encoder.encode(
            frames=self._rendered_frames(request.project, timeline, total_frames),
            canvas=self._canvas,
            spec=self._encoding,
            destination=request.destination,
            audio_reference=request.project.audio_reference,
        )

        return RenderVideoOutput(
            destination=request.destination,
            frame_count=total_frames,
            duration_seconds=timeline.total_seconds,
        )

    def _rendered_frames(
        self,
        project: VideoProject,
        timeline: SceneTimeline,
        total_frames: int,
    ) -> Iterator[FrameImage]:
        for plan in timeline.plan_frames():
            yield self._frame_renderer.render(project, plan, self._canvas, self._style)
            self._progress.frame_rendered(plan.frame_index, total_frames)
