from dataclasses import dataclass


@dataclass(frozen=True)
class EncodingSpec:
    video_codec: str
    preset: str
    constant_rate_factor: int
    pixel_format: str
    audio_codec: str
    audio_bitrate: str
