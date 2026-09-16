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
    render.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_DIRECTORY,
        help="directory holding base.yml and the environment overrides",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        container = Container(config_directory=arguments.config)
        result = container.render_command().execute(arguments.project, arguments.output)
    except (MissingSettingError, InvalidProjectDocumentError, VideoError) as failure:
        print(f"{type(failure).__name__}: {failure}", file=sys.stderr)
        return EXIT_FAILURE

    print(
        f"{result.destination}: {result.frame_count} frames, {result.duration_seconds:.2f} seconds"
    )
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
