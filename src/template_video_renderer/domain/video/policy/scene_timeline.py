from collections.abc import Iterator

from template_video_renderer.domain.video.entity.video_project import VideoProject
from template_video_renderer.domain.video.value.frame_plan import FramePlan
from template_video_renderer.domain.video.value.frame_rate import FrameRate
from template_video_renderer.domain.video.value.opacity import Opacity
from template_video_renderer.domain.video.value.scene_layer import SceneLayer
from template_video_renderer.domain.video.value.timing_spec import TimingSpec

FIRST_SCENE_INDEX = 0
PROGRESS_COMPLETE = 1.0


class SceneTimeline:
    def __init__(self, project: VideoProject, timing: TimingSpec, frame_rate: FrameRate) -> None:
        self._project = project
        self._timing = timing
        self._frame_rate = frame_rate

    @property
    def total_seconds(self) -> float:
        overlap = self._timing.transition_seconds * (self._project.scene_count - 1)
        return self._project.scene_count * self._timing.scene_seconds - overlap

    @property
    def total_frames(self) -> int:
        return self._frame_rate.frames_in(self.total_seconds)

    def plan_frames(self) -> Iterator[FramePlan]:
        for frame_index in range(self.total_frames):
            yield self.plan_frame(frame_index)

    def plan_frame(self, frame_index: int) -> FramePlan:
        moment = self._frame_rate.seconds_at(frame_index)
        layers = tuple(
            self._layer_for(scene_index, moment)
            for scene_index in self._visible_scene_indexes(moment)
        )
        return FramePlan(frame_index=frame_index, layers=layers)

    def _scene_start(self, scene_index: int) -> float:
        step = self._timing.scene_seconds - self._timing.transition_seconds
        return scene_index * step

    def _visible_scene_indexes(self, moment: float) -> list[int]:
        visible = [
            scene_index
            for scene_index in range(self._project.scene_count)
            if self._scene_start(scene_index)
            <= moment
            < self._scene_start(scene_index) + self._timing.scene_seconds
        ]
        return visible or [self._project.scene_count - 1]

    def _layer_for(self, scene_index: int, moment: float) -> SceneLayer:
        elapsed = moment - self._scene_start(scene_index)
        return SceneLayer(
            scene_index=scene_index,
            scene_opacity=self._scene_opacity(scene_index, elapsed),
            title_opacity=self._text_opacity(elapsed, self._timing.title_delay_seconds),
            subtitle_opacity=self._text_opacity(elapsed, self._timing.subtitle_delay_seconds),
            accent_progress=self._accent_progress(elapsed),
        )

    def _scene_opacity(self, scene_index: int, elapsed: float) -> Opacity:
        if scene_index == FIRST_SCENE_INDEX or self._timing.transition_seconds == 0:
            return Opacity(PROGRESS_COMPLETE)
        return Opacity.clamped(elapsed / self._timing.transition_seconds)

    def _text_opacity(self, elapsed: float, delay: float) -> Opacity:
        return Opacity.clamped((elapsed - delay) / self._timing.text_fade_seconds)

    def _accent_progress(self, elapsed: float) -> float:
        start = self._timing.subtitle_delay_seconds
        span = max(self._timing.scene_seconds - start, self._timing.text_fade_seconds)
        return min(max((elapsed - start) / span, 0.0), PROGRESS_COMPLETE)
