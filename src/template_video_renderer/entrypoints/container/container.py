from pathlib import Path

from template_video_renderer.adapters.inbound.cli.render_command import RenderCommand
from template_video_renderer.adapters.outbound.encoding.ffmpeg_video_encoder import (
    FfmpegVideoEncoder,
)
from template_video_renderer.adapters.outbound.rendering.pillow_frame_renderer import (
    PillowFrameRenderer,
)
from template_video_renderer.adapters.outbound.reporting.logging_progress_reporter import (
    LoggingProgressReporter,
)
from template_video_renderer.application.video.usecase.render_video_use_case import (
    RenderVideoUseCase,
)
from template_video_renderer.entrypoints.settings.app_settings import AppSettings
from template_video_renderer.entrypoints.settings.settings_loader import SettingsLoader
from template_video_renderer.infrastructure.logging.logging_setup import configure_logging


class Container:
    def __init__(self, config_directory: Path) -> None:
        self._settings = SettingsLoader(config_directory).load()
        self._logger = configure_logging(self._settings.logging_level)

    @property
    def settings(self) -> AppSettings:
        return self._settings

    def render_command(self) -> RenderCommand:
        return RenderCommand(use_case=self._render_video_use_case())

    def _render_video_use_case(self) -> RenderVideoUseCase:
        return RenderVideoUseCase(
            frame_renderer=PillowFrameRenderer(),
            video_encoder=FfmpegVideoEncoder(binary=self._settings.ffmpeg_binary),
            canvas=self._settings.canvas,
            style=self._settings.style,
            timing=self._settings.timing,
            encoding=self._settings.encoding,
            progress=LoggingProgressReporter(self._logger),
        )
