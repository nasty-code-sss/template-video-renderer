from pathlib import Path

import pytest

from template_video_renderer.adapters.inbound.cli.batch_render_command import BatchRenderCommand
from template_video_renderer.adapters.inbound.cli.render_command import RenderCommand
from template_video_renderer.adapters.mapper.invalid_project_document_error import (
    InvalidProjectDocumentError,
)
from template_video_renderer.application.video.dto.render_video_output import RenderVideoOutput
from template_video_renderer.domain.video.error.encoding_failed_error import EncodingFailedError


class RecordingRenderCommand(RenderCommand):
    def __init__(self, broken_projects: frozenset[str] = frozenset()) -> None:
        self._broken_projects = broken_projects
        self.rendered: list[Path] = []

    def execute(self, project_path: Path, destination: Path) -> RenderVideoOutput:
        if project_path.stem in self._broken_projects:
            raise InvalidProjectDocumentError("scene 1: field 'title' is missing")
        self.rendered.append(destination)
        return RenderVideoOutput(destination=str(destination), frame_count=30, duration_seconds=1.0)


def write_projects(folder: Path, names: list[str]) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    for name in names:
        (folder / f"{name}.json").write_text("{}", encoding="utf-8")
    return folder


def test_every_project_of_the_folder_becomes_its_own_file(tmp_path: Path) -> None:
    projects = write_projects(tmp_path / "projects", ["first", "second", "third"])
    render_command = RecordingRenderCommand()

    report = BatchRenderCommand(render_command).execute(projects, tmp_path / "out")

    assert report.rendered_count == 3
    assert report.has_failures is False
    assert render_command.rendered == [
        tmp_path / "out" / "first.mp4",
        tmp_path / "out" / "second.mp4",
        tmp_path / "out" / "third.mp4",
    ]


def test_one_broken_project_does_not_stop_the_others(tmp_path: Path) -> None:
    projects = write_projects(tmp_path / "projects", ["first", "second", "third"])
    render_command = RecordingRenderCommand(broken_projects=frozenset({"second"}))

    report = BatchRenderCommand(render_command).execute(projects, tmp_path / "out")

    assert report.planned_count == 3
    assert report.rendered_count == 2
    assert report.failed_count == 1
    assert render_command.rendered == [
        tmp_path / "out" / "first.mp4",
        tmp_path / "out" / "third.mp4",
    ]


def test_report_names_the_project_that_failed(tmp_path: Path) -> None:
    projects = write_projects(tmp_path / "projects", ["good", "wrong"])
    render_command = RecordingRenderCommand(broken_projects=frozenset({"wrong"}))

    report = BatchRenderCommand(render_command).execute(projects, tmp_path / "out")

    failed = [entry for entry in report.entries if not entry.succeeded]
    assert [entry.project_path.name for entry in failed] == ["wrong.json"]
    assert failed[0].failure == "InvalidProjectDocumentError: scene 1: field 'title' is missing"


def test_encoding_failure_is_collected_like_any_other(tmp_path: Path) -> None:
    class FailingRenderCommand(RenderCommand):
        def __init__(self) -> None:
            pass

        def execute(self, project_path: Path, destination: Path) -> RenderVideoOutput:
            raise EncodingFailedError("ffmpeg failed: no space left on device")

    projects = write_projects(tmp_path / "projects", ["only"])

    report = BatchRenderCommand(FailingRenderCommand()).execute(projects, tmp_path / "out")

    assert report.rendered_count == 0
    assert report.entries[0].failure is not None
    assert "EncodingFailedError" in report.entries[0].failure


def test_missing_folder_is_reported_before_any_render(tmp_path: Path) -> None:
    with pytest.raises(InvalidProjectDocumentError, match="was not found"):
        BatchRenderCommand(RecordingRenderCommand()).execute(tmp_path / "absent", tmp_path / "out")


def test_folder_without_projects_is_reported(tmp_path: Path) -> None:
    empty = tmp_path / "projects"
    empty.mkdir()

    with pytest.raises(InvalidProjectDocumentError, match="holds no"):
        BatchRenderCommand(RecordingRenderCommand()).execute(empty, tmp_path / "out")
