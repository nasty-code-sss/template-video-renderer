import logging

PROGRESS_STEP_RATIO = 0.1


class LoggingProgressReporter:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        self._next_reported_frame = 0
        self._step = 1

    def frames_planned(self, total_frames: int, duration_seconds: float) -> None:
        self._step = max(int(total_frames * PROGRESS_STEP_RATIO), 1)
        self._next_reported_frame = 0
        self._logger.info(
            "planned %s frames for %.2f seconds of video", total_frames, duration_seconds
        )

    def frame_rendered(self, frame_index: int, total_frames: int) -> None:
        if frame_index < self._next_reported_frame:
            return
        self._next_reported_frame += self._step
        self._logger.info("rendered frame %s of %s", frame_index + 1, total_frames)

    def encoding_started(self, destination: str) -> None:
        self._logger.info("encoding into %s", destination)
