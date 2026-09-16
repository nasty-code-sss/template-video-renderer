from pathlib import Path
from typing import Any

from template_video_renderer.adapters.mapper.invalid_project_document_error import (
    InvalidProjectDocumentError,
)
from template_video_renderer.domain.video.entity.scene import Scene
from template_video_renderer.domain.video.entity.video_project import VideoProject

NAME_FIELD = "name"
SCENES_FIELD = "scenes"
TITLE_FIELD = "title"
SUBTITLE_FIELD = "subtitle"
IMAGE_FIELD = "image"
AUDIO_FIELD = "audio"


class VideoProjectMapper:
    def __init__(self, asset_root: Path) -> None:
        self._asset_root = asset_root

    def to_domain(self, document: dict[str, Any]) -> VideoProject:
        self._require_mapping(document)
        raw_scenes = self._require_scenes(document)
        scenes = tuple(
            self._scene_to_domain(raw_scene, position)
            for position, raw_scene in enumerate(raw_scenes)
        )
        return VideoProject(
            name=self._require_text(document, NAME_FIELD, "project"),
            scenes=scenes,
            audio_reference=self._optional_asset(document, AUDIO_FIELD, "project"),
        )

    def _require_mapping(self, document: object) -> None:
        if not isinstance(document, dict):
            raise InvalidProjectDocumentError(
                f"project document must be an object, got {type(document).__name__}"
            )

    def _require_scenes(self, document: dict[str, Any]) -> list[Any]:
        raw_scenes = document.get(SCENES_FIELD)
        if not isinstance(raw_scenes, list):
            raise InvalidProjectDocumentError(
                f"project field '{SCENES_FIELD}' must be a list of scenes"
            )
        return raw_scenes

    def _scene_to_domain(self, raw_scene: Any, position: int) -> Scene:
        location = f"scene {position + 1}"
        if not isinstance(raw_scene, dict):
            raise InvalidProjectDocumentError(f"{location} must be an object")
        return Scene(
            title=self._require_text(raw_scene, TITLE_FIELD, location),
            subtitle=self._optional_text(raw_scene, SUBTITLE_FIELD, location),
            image_reference=self._optional_asset(raw_scene, IMAGE_FIELD, location),
        )

    def _require_text(self, source: dict[str, Any], field: str, location: str) -> str:
        value = source.get(field)
        if not isinstance(value, str) or not value.strip():
            raise InvalidProjectDocumentError(
                f"{location}: field '{field}' is required and must be a non-empty string"
            )
        return value

    def _optional_text(self, source: dict[str, Any], field: str, location: str) -> str:
        value = source.get(field, "")
        if not isinstance(value, str):
            raise InvalidProjectDocumentError(f"{location}: field '{field}' must be a string")
        return value

    def _optional_asset(self, source: dict[str, Any], field: str, location: str) -> str | None:
        value = source.get(field)
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            raise InvalidProjectDocumentError(
                f"{location}: field '{field}' must be a path to an existing file"
            )
        resolved = self._resolve(value)
        if not resolved.is_file():
            raise InvalidProjectDocumentError(f"{location}: file '{value}' was not found")
        return str(resolved)

    def _resolve(self, reference: str) -> Path:
        candidate = Path(reference)
        if candidate.is_absolute():
            return candidate
        return (self._asset_root / candidate).resolve()
