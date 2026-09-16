import json
import shutil
import subprocess
from pathlib import Path

import pytest

from template_video_renderer.entrypoints.cli.main import main

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIRECTORY = PROJECT_ROOT / "config"
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None, reason="ffmpeg is required for end to end rendering"
)


def probe(field: str, target: Path) -> str:
    output = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            field,
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(target),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return output.stdout.strip()


def write_project(folder: Path, scene_count: int) -> Path:
    document = {
        "name": "end to end",
        "scenes": [
            {"title": f"Сцена {number + 1}", "subtitle": "проверка"}
            for number in range(scene_count)
        ],
    }
    folder.mkdir(parents=True, exist_ok=True)
    project_path = folder / "project.json"
    project_path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
    return project_path


def render(project_path: Path, destination: Path) -> int:
    return main(
        [
            "render",
            "--project",
            str(project_path),
            "--output",
            str(destination),
            "--config",
            str(CONFIG_DIRECTORY),
        ]
    )


def test_render_produces_a_playable_file_of_expected_size(tmp_path: Path) -> None:
    destination = tmp_path / "out.mp4"

    exit_code = render(write_project(tmp_path, scene_count=2), destination)

    assert exit_code == EXIT_SUCCESS
    assert destination.stat().st_size > 0
    assert probe("stream=width", destination) == "1920"
    assert probe("stream=height", destination) == "1080"


def test_render_length_grows_with_the_number_of_scenes(tmp_path: Path) -> None:
    short_target = tmp_path / "short.mp4"
    long_target = tmp_path / "long.mp4"

    render(write_project(tmp_path / "short", scene_count=1), short_target)
    render(write_project(tmp_path / "long", scene_count=3), long_target)

    assert int(probe("stream=nb_frames", long_target)) > int(
        probe("stream=nb_frames", short_target)
    )


def test_broken_project_fails_without_leaving_a_video(tmp_path: Path) -> None:
    project_path = tmp_path / "broken.json"
    project_path.write_text('{"name": "broken", "scenes": [{"subtitle": "no title"}]}', "utf-8")
    destination = tmp_path / "broken.mp4"

    exit_code = render(project_path, destination)

    assert exit_code == EXIT_FAILURE
    assert destination.exists() is False
