from dataclasses import dataclass

from template_video_renderer.domain.video.error.invalid_canvas_error import InvalidCanvasError

MINIMUM_SIDE_PIXELS = 16
EVEN_DIVISOR = 2


@dataclass(frozen=True)
class Resolution:
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.width < MINIMUM_SIDE_PIXELS or self.height < MINIMUM_SIDE_PIXELS:
            raise InvalidCanvasError(
                f"resolution {self.width}x{self.height} is below {MINIMUM_SIDE_PIXELS} pixels"
            )
        if self.width % EVEN_DIVISOR or self.height % EVEN_DIVISOR:
            raise InvalidCanvasError(
                f"resolution {self.width}x{self.height} must have even sides for yuv420p"
            )

    @property
    def is_portrait(self) -> bool:
        return self.height > self.width

    def scaled_height(self, ratio: float) -> int:
        return int(self.height * ratio)

    def scaled_width(self, ratio: float) -> int:
        return int(self.width * ratio)
