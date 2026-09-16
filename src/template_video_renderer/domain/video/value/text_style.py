from dataclasses import dataclass


@dataclass(frozen=True)
class TextStyle:
    font_reference: str
    size: int
    color: str
