from dataclasses import dataclass

from template_video_renderer.domain.video.error.invalid_timing_error import InvalidTimingError

MINIMUM_FRAMES_PER_SECOND = 1
MAXIMUM_FRAMES_PER_SECOND = 120


@dataclass(frozen=True)
class FrameRate:
    frames_per_second: int

    def __post_init__(self) -> None:
        if not MINIMUM_FRAMES_PER_SECOND <= self.frames_per_second <= MAXIMUM_FRAMES_PER_SECOND:
            raise InvalidTimingError(
                f"frame rate {self.frames_per_second} is outside "
                f"{MINIMUM_FRAMES_PER_SECOND}-{MAXIMUM_FRAMES_PER_SECOND}"
            )

    def frames_in(self, seconds: float) -> int:
        return int(round(seconds * self.frames_per_second))

    def seconds_at(self, frame_index: int) -> float:
        return frame_index / self.frames_per_second
