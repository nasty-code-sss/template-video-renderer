import subprocess
import tempfile
from collections.abc import Iterable
from typing import IO

from template_video_renderer.domain.video.error.encoding_failed_error import EncodingFailedError
from template_video_renderer.domain.video.value.canvas_spec import CanvasSpec
from template_video_renderer.domain.video.value.encoding_spec import EncodingSpec
from template_video_renderer.domain.video.value.frame_image import FrameImage

RAW_PIXEL_FORMAT = "rgb24"
STDIN_INPUT = "pipe:0"
STDERR_TAIL_LINES = 12


class FfmpegVideoEncoder:
    def __init__(self, binary: str) -> None:
        self._binary = binary

    def encode(
        self,
        frames: Iterable[FrameImage],
        canvas: CanvasSpec,
        spec: EncodingSpec,
        destination: str,
        audio_reference: str | None,
    ) -> None:
        with tempfile.TemporaryFile() as diagnostics:
            process = subprocess.Popen(
                self._build_command(canvas, spec, destination, audio_reference),
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=diagnostics,
            )
            if process.stdin is None:
                raise EncodingFailedError("ffmpeg did not provide an input stream")

            try:
                for frame in frames:
                    process.stdin.write(frame.payload)
            except BrokenPipeError as failure:
                process.wait()
                raise EncodingFailedError(self._failure_text(diagnostics)) from failure
            finally:
                process.stdin.close()

            if process.wait() != 0:
                raise EncodingFailedError(self._failure_text(diagnostics))

    def _build_command(
        self,
        canvas: CanvasSpec,
        spec: EncodingSpec,
        destination: str,
        audio_reference: str | None,
    ) -> list[str]:
        command = [
            self._binary,
            "-y",
            "-hide_banner",
            "-f",
            "rawvideo",
            "-pix_fmt",
            RAW_PIXEL_FORMAT,
            "-s",
            f"{canvas.resolution.width}x{canvas.resolution.height}",
            "-r",
            str(canvas.frame_rate.frames_per_second),
            "-i",
            STDIN_INPUT,
        ]
        if audio_reference is not None:
            command += ["-i", audio_reference, "-shortest"]
        command += [
            "-c:v",
            spec.video_codec,
            "-preset",
            spec.preset,
            "-crf",
            str(spec.constant_rate_factor),
            "-pix_fmt",
            spec.pixel_format,
        ]
        if audio_reference is not None:
            command += ["-c:a", spec.audio_codec, "-b:a", spec.audio_bitrate]
        command.append(destination)
        return command

    def _failure_text(self, diagnostics: IO[bytes]) -> str:
        diagnostics.seek(0)
        reported = diagnostics.read().decode("utf-8", errors="replace").strip().splitlines()
        if not reported:
            return "ffmpeg failed without diagnostics"
        return "ffmpeg failed: " + " | ".join(reported[-STDERR_TAIL_LINES:])
