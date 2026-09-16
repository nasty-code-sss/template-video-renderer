import json
from pathlib import Path
from typing import Any

from template_video_renderer.adapters.mapper.invalid_project_document_error import (
    InvalidProjectDocumentError,
)
from template_video_renderer.adapters.mapper.video_project_mapper import VideoProjectMapper
from template_video_renderer.application.video.dto.render_video_input import RenderVideoInput
from template_video_renderer.application.video.dto.render_video_output import RenderVideoOutput
from template_video_renderer.application.video.usecase.render_video_use_case import (
    RenderVideoUseCase,
)


class RenderCommand:
    def __init__(self, use_case: RenderVideoUseCase) -> None:
        self._use_case = use_case

    def execute(self, project_path: Path, destination: Path) -> RenderVideoOutput:
        document = self._read_document(project_path)
        mapper = VideoProjectMapper(asset_root=project_path.parent)
        project = mapper.to_domain(document)
        destination.parent.mkdir(parents=True, exist_ok=True)
        return self._use_case.execute(
            RenderVideoInput(project=project, destination=str(destination))
        )

    def _read_document(self, project_path: Path) -> dict[str, Any]:
        if not project_path.is_file():
            raise InvalidProjectDocumentError(f"project file '{project_path}' was not found")
        try:
            parsed: object = json.loads(project_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as failure:
            raise InvalidProjectDocumentError(
                f"project file '{project_path}' is not valid JSON: {failure}"
            ) from failure
        if not isinstance(parsed, dict):
            raise InvalidProjectDocumentError(
                f"project file '{project_path}' must contain an object at the top level"
            )
        return parsed
