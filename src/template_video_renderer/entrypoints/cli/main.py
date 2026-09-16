import argparse
import sys
from pathlib import Path

from template_video_renderer.adapters.mapper.invalid_project_document_error import (
    InvalidProjectDocumentError,
)
from template_video_renderer.domain.video.error.video_error import VideoError
from template_video_renderer.entrypoints.container.container import Container
from template_video_renderer.entrypoints.settings.missing_setting_error import MissingSettingError

RENDER_COMMAND_NAME = "render"
BATCH_COMMAND_NAME = "batch"
DEFAULT_CONFIG_DIRECTORY = Path("config")
EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="template-video-renderer",
        description="Renders a video file from a JSON scene description and a YAML template",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    render = commands.add_parser(RENDER_COMMAND_NAME, help="render one project into a video file")
    render.add_argument("--project", required=True, type=Path, help="path to the project JSON")
    render.add_argument("--output", required=True, type=Path, help="path to the resulting file")
    _add_config_argument(render)
    batch = commands.add_parser(
        BATCH_COMMAND_NAME, help="render every project of a folder into a video file"
    )
    batch.add_argument(
        "--projects", required=True, type=Path, help="directory holding the project JSON files"
    )
    batch.add_argument(
        "--output-dir", required=True, type=Path, help="directory for the resulting files"
    )
    _add_config_argument(batch)
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        container = Container(config_directory=arguments.config)
        if arguments.command == BATCH_COMMAND_NAME:
            return _run_batch(container, arguments.projects, arguments.output_dir)
        return _run_render(container, arguments.project, arguments.output)
    except (MissingSettingError, InvalidProjectDocumentError, VideoError) as failure:
        print(f"{type(failure).__name__}: {failure}", file=sys.stderr)
        return EXIT_FAILURE


def _add_config_argument(command: argparse.ArgumentParser) -> None:
    command.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_DIRECTORY,
        help="directory holding base.yml and the environment overrides",
    )


def _run_render(container: Container, project_path: Path, destination: Path) -> int:
    result = container.render_command().execute(project_path, destination)
    print(
        f"{result.destination}: {result.frame_count} frames, {result.duration_seconds:.2f} seconds"
    )
    return EXIT_SUCCESS


def _run_batch(container: Container, projects_directory: Path, output_directory: Path) -> int:
    report = container.batch_render_command().execute(projects_directory, output_directory)
    for entry in report.entries:
        if entry.output is None:
            print(f"{entry.project_path.name}: {entry.failure}", file=sys.stderr)
            continue
        print(
            f"{entry.project_path.name} -> {entry.output.destination}: "
            f"{entry.output.frame_count} frames, {entry.output.duration_seconds:.2f} seconds"
        )
    print(f"rendered {report.rendered_count} of {report.planned_count} projects")
    return EXIT_FAILURE if report.has_failures else EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
