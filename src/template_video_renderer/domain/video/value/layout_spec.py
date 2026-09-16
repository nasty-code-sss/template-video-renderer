from dataclasses import dataclass


@dataclass(frozen=True)
class LayoutSpec:
    safe_margin_ratio: float
    title_baseline_ratio: float
    subtitle_baseline_ratio: float
    image_height_ratio: float
    accent_bar_width_ratio: float
    accent_bar_height: int
