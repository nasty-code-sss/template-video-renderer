from dataclasses import dataclass


@dataclass(frozen=True)
class FrameImage:
    payload: bytes
