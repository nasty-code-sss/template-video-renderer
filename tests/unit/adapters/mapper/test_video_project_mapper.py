from pathlib import Path

import pytest

from template_video_renderer.adapters.mapper.invalid_project_document_error import (
    InvalidProjectDocumentError,
)
from template_video_renderer.adapters.mapper.video_project_mapper import VideoProjectMapper


def mapper_for(tmp_path: Path) -> VideoProjectMapper:
    return VideoProjectMapper(asset_root=tmp_path)


def test_valid_document_becomes_project_with_all_scenes(tmp_path: Path) -> None:
    document = {
        "name": "promo",
        "scenes": [
            {"title": "first", "subtitle": "one"},
            {"title": "second", "subtitle": "two"},
        ],
    }

    project = mapper_for(tmp_path).to_domain(document)

    assert project.name == "promo"
    assert project.scene_count == 2
    assert project.scene_at(1).title == "second"


def test_scene_without_subtitle_gets_empty_subtitle(tmp_path: Path) -> None:
    document = {"name": "promo", "scenes": [{"title": "only title"}]}

    project = mapper_for(tmp_path).to_domain(document)

    assert project.scene_at(0).subtitle == ""


def test_scene_without_title_is_rejected_naming_the_scene(tmp_path: Path) -> None:
    document = {"name": "promo", "scenes": [{"title": "fine"}, {"subtitle": "no title here"}]}

    with pytest.raises(InvalidProjectDocumentError, match="scene 2"):
        mapper_for(tmp_path).to_domain(document)


def test_document_without_scenes_list_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(InvalidProjectDocumentError, match="scenes"):
        mapper_for(tmp_path).to_domain({"name": "promo"})


def test_missing_image_file_is_reported_before_rendering(tmp_path: Path) -> None:
    document = {
        "name": "promo",
        "scenes": [{"title": "with image", "image": "absent.png"}],
    }

    with pytest.raises(InvalidProjectDocumentError, match="absent.png"):
        mapper_for(tmp_path).to_domain(document)


def test_existing_image_is_resolved_against_the_project_folder(tmp_path: Path) -> None:
    picture = tmp_path / "shot.png"
    picture.write_bytes(b"not a real image but a real file")
    document = {"name": "promo", "scenes": [{"title": "with image", "image": "shot.png"}]}

    project = mapper_for(tmp_path).to_domain(document)

    assert project.scene_at(0).image_reference == str(picture.resolve())


def test_document_that_is_not_an_object_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(InvalidProjectDocumentError):
        mapper_for(tmp_path).to_domain(["not", "an", "object"])  # type: ignore[arg-type]
