import os
from pathlib import Path
from typing import Any

import yaml

from template_video_renderer.domain.video.value.canvas_spec import CanvasSpec
from template_video_renderer.domain.video.value.encoding_spec import EncodingSpec
from template_video_renderer.domain.video.value.frame_rate import FrameRate
from template_video_renderer.domain.video.value.layout_spec import LayoutSpec
from template_video_renderer.domain.video.value.resolution import Resolution
from template_video_renderer.domain.video.value.style_spec import StyleSpec
from template_video_renderer.domain.video.value.text_style import TextStyle
from template_video_renderer.domain.video.value.timing_spec import TimingSpec
from template_video_renderer.entrypoints.settings.app_settings import AppSettings
from template_video_renderer.entrypoints.settings.missing_setting_error import MissingSettingError

ENVIRONMENT_VARIABLE = "APP_ENV"
FFMPEG_VARIABLE = "FFMPEG_BINARY"
DEFAULT_ENVIRONMENT = "dev"
DEFAULT_FFMPEG_BINARY = "ffmpeg"
BASE_CONFIG_NAME = "base.yml"
KNOWN_ENVIRONMENTS = ("dev", "stage", "prod")


class SettingsLoader:
    def __init__(self, config_directory: Path) -> None:
        self._config_directory = config_directory

    def load(self) -> AppSettings:
        environment = os.environ.get(ENVIRONMENT_VARIABLE, DEFAULT_ENVIRONMENT)
        if environment not in KNOWN_ENVIRONMENTS:
            raise MissingSettingError(
                f"{ENVIRONMENT_VARIABLE}='{environment}' is not one of {KNOWN_ENVIRONMENTS}"
            )
        merged = self._merge(
            self._read(self._config_directory / BASE_CONFIG_NAME),
            self._read(self._config_directory / f"{environment}.yml"),
        )
        try:
            return AppSettings(
                environment=environment,
                ffmpeg_binary=os.environ.get(FFMPEG_VARIABLE) or DEFAULT_FFMPEG_BINARY,
                logging_level=self._section(merged, "logging")["level"],
                canvas=self._canvas(merged),
                style=self._style(merged),
                timing=self._timing(merged),
                encoding=self._encoding(merged),
            )
        except KeyError as absent:
            raise MissingSettingError(
                f"configuration key {absent} is missing in base.yml or {environment}.yml"
            ) from absent

    def _read(self, path: Path) -> dict[str, Any]:
        if not path.is_file():
            raise MissingSettingError(f"configuration file '{path}' was not found")
        content = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(content, dict):
            raise MissingSettingError(f"configuration file '{path}' must contain a mapping")
        return content

    def _merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        merged = dict(base)
        for key, value in override.items():
            existing = merged.get(key)
            if isinstance(existing, dict) and isinstance(value, dict):
                merged[key] = self._merge(existing, value)
            else:
                merged[key] = value
        return merged

    def _section(self, source: dict[str, Any], name: str) -> dict[str, Any]:
        section = source.get(name)
        if not isinstance(section, dict):
            raise MissingSettingError(f"configuration section '{name}' is missing")
        return section

    def _canvas(self, merged: dict[str, Any]) -> CanvasSpec:
        canvas = self._section(merged, "canvas")
        return CanvasSpec(
            resolution=Resolution(width=canvas["width"], height=canvas["height"]),
            frame_rate=FrameRate(frames_per_second=canvas["frames_per_second"]),
            background_color=canvas["background_color"],
        )

    def _style(self, merged: dict[str, Any]) -> StyleSpec:
        typography = self._section(merged, "typography")
        layout = self._section(merged, "layout")
        return StyleSpec(
            title=self._text_style(typography["title"]),
            subtitle=self._text_style(typography["subtitle"]),
            accent_color=typography["accent_color"],
            layout=LayoutSpec(
                safe_margin_ratio=layout["safe_margin_ratio"],
                title_baseline_ratio=layout["title_baseline_ratio"],
                subtitle_baseline_ratio=layout["subtitle_baseline_ratio"],
                image_height_ratio=layout["image_height_ratio"],
                accent_bar_width_ratio=layout["accent_bar_width_ratio"],
                accent_bar_height=layout["accent_bar_height"],
            ),
        )

    def _text_style(self, source: dict[str, Any]) -> TextStyle:
        return TextStyle(
            font_reference=source["font_path"],
            size=source["size"],
            color=source["color"],
        )

    def _timing(self, merged: dict[str, Any]) -> TimingSpec:
        timing = self._section(merged, "timing")
        return TimingSpec(
            scene_seconds=timing["scene_seconds"],
            transition_seconds=timing["transition_seconds"],
            title_delay_seconds=timing["title_delay_seconds"],
            subtitle_delay_seconds=timing["subtitle_delay_seconds"],
            text_fade_seconds=timing["text_fade_seconds"],
        )

    def _encoding(self, merged: dict[str, Any]) -> EncodingSpec:
        encoding = self._section(merged, "encoding")
        return EncodingSpec(
            video_codec=encoding["video_codec"],
            preset=encoding["preset"],
            constant_rate_factor=encoding["constant_rate_factor"],
            pixel_format=encoding["pixel_format"],
            audio_codec=encoding["audio_codec"],
            audio_bitrate=encoding["audio_bitrate"],
        )
