from dataclasses import dataclass


@dataclass(frozen=True)
class Scene:
    title: str
    subtitle: str
    image_reference: str | None

    @property
    def has_image(self) -> bool:
        return self.image_reference is not None
