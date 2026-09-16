from dataclasses import dataclass

from template_video_renderer.domain.video.error.invalid_timing_error import InvalidTimingError


@dataclass(frozen=True)
class TimingSpec:
    scene_seconds: float
    transition_seconds: float
    title_delay_seconds: float
    subtitle_delay_seconds: float
    text_fade_seconds: float

    def __post_init__(self) -> None:
        if self.scene_seconds <= 0:
            raise InvalidTimingError("scene duration must be positive")
        if self.text_fade_seconds <= 0:
            raise InvalidTimingError("text fade duration must be positive")
        if self.transition_seconds < 0:
            raise InvalidTimingError("transition duration cannot be negative")
        if self.transition_seconds >= self.scene_seconds:
            raise InvalidTimingError(
                "transition cannot be longer than the scene it transitions from"
            )
        if self.title_delay_seconds < 0 or self.subtitle_delay_seconds < 0:
            raise InvalidTimingError("text delays cannot be negative")
