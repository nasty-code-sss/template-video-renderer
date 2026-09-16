import json
import shutil
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


def write_project(folder: Path, name: str, scene_count: int) -> None:
    document = {
        "name": name,
        "scenes": [
            {"title": f"{name} {number + 1}", "subtitle": "пакетный прогон"}
            for number in range(scene_count)
        ],
    }
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{name}.json").write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")


def render_batch(projects: Path, output_directory: Path) -> int:
    return main(
        [
            "batch",
            "--projects",
            str(projects),
            "--output-dir",
            str(output_directory),
            "--config",
            str(CONFIG_DIRECTORY),
        ]
    )


def test_batch_turns_every_project_into_its_own_video(tmp_path: Path) -> None:
    projects = tmp_path / "projects"
    output_directory = tmp_path / "out"
    write_project(projects, "first", scene_count=1)
    write_project(projects, "second", scene_count=1)

    exit_code = render_batch(projects, output_directory)

    assert exit_code == EXIT_SUCCESS
    assert (output_directory / "first.mp4").stat().st_size > 0
    assert (output_directory / "second.mp4").stat().st_size > 0


def test_broken_project_fails_alone_and_the_rest_is_rendered(tmp_path: Path) -> None:
    projects = tmp_path / "projects"
    output_directory = tmp_path / "out"
    write_project(projects, "good", scene_count=1)
    (projects / "broken.json").write_text(
        '{"name": "broken", "scenes": [{"subtitle": "no title"}]}', encoding="utf-8"
    )

    exit_code = render_batch(projects, output_directory)

    assert exit_code == EXIT_FAILURE
    assert (output_directory / "good.mp4").stat().st_size > 0
    assert (output_directory / "broken.mp4").exists() is False


def test_batch_reports_each_project_and_the_total(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    projects = tmp_path / "projects"
    write_project(projects, "first", scene_count=1)
    write_project(projects, "second", scene_count=1)

    render_batch(projects, tmp_path / "out")

    reported = capsys.readouterr().out
    assert "first.json -> " in reported
    assert "second.json -> " in reported
    assert "rendered 2 of 2 projects" in reported
