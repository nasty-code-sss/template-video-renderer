from dataclasses import dataclass

from template_video_renderer.adapters.inbound.cli.batch_render_entry import BatchRenderEntry


@dataclass(frozen=True)
class BatchRenderReport:
    entries: tuple[BatchRenderEntry, ...]

    @property
    def planned_count(self) -> int:
        return len(self.entries)

    @property
    def rendered_count(self) -> int:
        return sum(1 for entry in self.entries if entry.succeeded)

    @property
    def failed_count(self) -> int:
        return self.planned_count - self.rendered_count

    @property
    def has_failures(self) -> bool:
        return self.failed_count > 0
