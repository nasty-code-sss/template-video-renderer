from dataclasses import dataclass

FULLY_TRANSPARENT = 0.0
FULLY_OPAQUE = 1.0
ALPHA_CHANNEL_MAXIMUM = 255


@dataclass(frozen=True)
class Opacity:
    value: float

    @staticmethod
    def clamped(value: float) -> "Opacity":
        return Opacity(max(FULLY_TRANSPARENT, min(FULLY_OPAQUE, value)))

    @property
    def is_invisible(self) -> bool:
        return self.value <= FULLY_TRANSPARENT

    @property
    def as_alpha_channel(self) -> int:
        return int(round(self.value * ALPHA_CHANNEL_MAXIMUM))
