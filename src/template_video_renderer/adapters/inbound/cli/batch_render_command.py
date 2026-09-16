from pathlib import Path

from template_video_renderer.adapters.inbound.cli.batch_render_entry import BatchRenderEntry
from template_video_renderer.adapters.inbound.cli.batch_render_report import BatchRenderReport
from template_video_renderer.adapters.inbound.cli.render_command import RenderCommand
from template_video_renderer.adapters.mapper.invalid_project_document_error import (
    InvalidProjectDocumentError,
)
from template_video_renderer.domain.video.error.video_error import VideoError

PROJECT_FILE_PATTERN = "*.json"
VIDEO_FILE_SUFFIX = ".mp4"


class BatchRenderCommand:
    def __init__(self, render_command: RenderCommand) -> None:
        self._render_command = render_command

    def execute(self, projects_directory: Path, output_directory: Path) -> BatchRenderReport:
        project_paths = self._collect_projects(projects_directory)
        output_directory.mkdir(parents=True, exist_ok=True)
        return BatchRenderReport(
            entries=tuple(
                self._render_one(project_path, self._destination(project_path, output_directory))
                for project_path in project_paths
            )
        )

    def _collect_projects(self, projects_directory: Path) -> list[Path]:
        if not projects_directory.is_dir():
            raise InvalidProjectDocumentError(
                f"projects directory '{projects_directory}' was not found"
            )
        found = sorted(projects_directory.glob(PROJECT_FILE_PATTERN))
        if not found:
            raise InvalidProjectDocumentError(
                f"projects directory '{projects_directory}' holds no {PROJECT_FILE_PATTERN} files"
            )
        return found

    def _destination(self, project_path: Path, output_directory: Path) -> Path:
        return output_directory / f"{project_path.stem}{VIDEO_FILE_SUFFIX}"

    def _render_one(self, project_path: Path, destination: Path) -> BatchRenderEntry:
        try:
            output = self._render_command.execute(project_path, destination)
        except (InvalidProjectDocumentError, VideoError) as failure:
            return BatchRenderEntry(
                project_path=project_path,
                destination=destination,
                output=None,
                failure=f"{type(failure).__name__}: {failure}",
            )
        return BatchRenderEntry(
            project_path=project_path,
            destination=destination,
            output=output,
            failure=None,
        )
