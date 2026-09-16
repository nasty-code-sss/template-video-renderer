from dataclasses import dataclass
from pathlib import Path

from template_video_renderer.application.video.dto.render_video_output import RenderVideoOutput


@dataclass(frozen=True)
class BatchRenderEntry:
    project_path: Path
    destination: Path
    output: RenderVideoOutput | None
    failure: str | None

    @property
    def succeeded(self) -> bool:
        return self.failure is None
