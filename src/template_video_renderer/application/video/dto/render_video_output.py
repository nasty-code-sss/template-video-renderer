from dataclasses import dataclass


@dataclass(frozen=True)
class RenderVideoOutput:
    destination: str
    frame_count: int
    duration_seconds: float
