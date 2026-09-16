from PIL import Image, ImageDraw, ImageFont

from template_video_renderer.domain.video.entity.scene import Scene
from template_video_renderer.domain.video.entity.video_project import VideoProject
from template_video_renderer.domain.video.error.scene_asset_missing_error import (
    SceneAssetMissingError,
)
from template_video_renderer.domain.video.value.canvas_spec import CanvasSpec
from template_video_renderer.domain.video.value.frame_image import FrameImage
from template_video_renderer.domain.video.value.frame_plan import FramePlan
from template_video_renderer.domain.video.value.scene_layer import SceneLayer
from template_video_renderer.domain.video.value.style_spec import StyleSpec
from template_video_renderer.domain.video.value.text_style import TextStyle

RGB_MODE = "RGB"
RGBA_MODE = "RGBA"
TRANSPARENT = (0, 0, 0, 0)
FULL_BLEND = 1.0


class PillowFrameRenderer:
    def __init__(self) -> None:
        self._fonts: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}
        self._images: dict[str, Image.Image] = {}

    def render(
        self,
        project: VideoProject,
        plan: FramePlan,
        canvas: CanvasSpec,
        style: StyleSpec,
    ) -> FrameImage:
        frame = Image.new(
            RGB_MODE,
            (canvas.resolution.width, canvas.resolution.height),
            canvas.background_color,
        )
        for layer in plan.layers:
            painted = self._paint_scene(project.scene_at(layer.scene_index), layer, canvas, style)
            frame = self._blend(frame, painted, layer)
        return FrameImage(payload=frame.tobytes())

    def _blend(self, frame: Image.Image, painted: Image.Image, layer: SceneLayer) -> Image.Image:
        if layer.scene_opacity.value >= FULL_BLEND:
            return painted
        if layer.scene_opacity.is_invisible:
            return frame
        return Image.blend(frame, painted, layer.scene_opacity.value)

    def _paint_scene(
        self,
        scene: Scene,
        layer: SceneLayer,
        canvas: CanvasSpec,
        style: StyleSpec,
    ) -> Image.Image:
        painted = Image.new(
            RGB_MODE,
            (canvas.resolution.width, canvas.resolution.height),
            canvas.background_color,
        )
        if scene.has_image:
            self._paste_image(painted, scene, canvas, style)

        overlay = Image.new(RGBA_MODE, painted.size, TRANSPARENT)
        draw = ImageDraw.Draw(overlay)
        self._draw_centered_text(
            draw,
            scene.title,
            style.title,
            layer.title_opacity.as_alpha_channel,
            canvas.resolution.scaled_height(style.layout.title_baseline_ratio),
            canvas.resolution.width,
        )
        self._draw_centered_text(
            draw,
            scene.subtitle,
            style.subtitle,
            layer.subtitle_opacity.as_alpha_channel,
            canvas.resolution.scaled_height(style.layout.subtitle_baseline_ratio),
            canvas.resolution.width,
        )
        self._draw_accent_bar(draw, layer, canvas, style)

        painted.paste(overlay, mask=overlay)
        return painted

    def _paste_image(
        self,
        painted: Image.Image,
        scene: Scene,
        canvas: CanvasSpec,
        style: StyleSpec,
    ) -> None:
        source = self._load_image(str(scene.image_reference))
        target_height = canvas.resolution.scaled_height(style.layout.image_height_ratio)
        ratio = target_height / source.height
        resized = source.resize((int(source.width * ratio), target_height))
        top = canvas.resolution.scaled_height(style.layout.safe_margin_ratio)
        left = (canvas.resolution.width - resized.width) // 2
        painted.paste(resized, (left, top), resized)

    def _draw_centered_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        style: TextStyle,
        alpha: int,
        baseline: int,
        canvas_width: int,
    ) -> None:
        if not text or alpha <= 0:
            return
        font = self._load_font(style.font_reference, style.size)
        box = draw.textbbox((0, 0), text, font=font)
        left = (canvas_width - box[2]) // 2
        draw.text((left, baseline), text, font=font, fill=self._with_alpha(style.color, alpha))

    def _draw_accent_bar(
        self,
        draw: ImageDraw.ImageDraw,
        layer: SceneLayer,
        canvas: CanvasSpec,
        style: StyleSpec,
    ) -> None:
        if layer.accent_progress <= 0:
            return
        full_width = canvas.resolution.scaled_width(style.layout.accent_bar_width_ratio)
        width = int(full_width * layer.accent_progress)
        left = (canvas.resolution.width - full_width) // 2
        top = canvas.resolution.height - canvas.resolution.scaled_height(
            style.layout.safe_margin_ratio
        )
        draw.rectangle(
            [left, top, left + width, top + style.layout.accent_bar_height],
            fill=self._with_alpha(style.accent_color, layer.subtitle_opacity.as_alpha_channel),
        )

    def _with_alpha(self, color: str, alpha: int) -> tuple[int, int, int, int]:
        red, green, blue = Image.new(RGB_MODE, (1, 1), color).getpixel((0, 0))  # type: ignore[misc]
        return red, green, blue, alpha

    def _load_font(self, reference: str, size: int) -> ImageFont.FreeTypeFont:
        key = (reference, size)
        if key not in self._fonts:
            try:
                self._fonts[key] = ImageFont.truetype(reference, size)
            except OSError as failure:
                raise SceneAssetMissingError(f"font '{reference}' could not be opened") from failure
        return self._fonts[key]

    def _load_image(self, reference: str) -> Image.Image:
        if reference not in self._images:
            try:
                self._images[reference] = Image.open(reference).convert(RGBA_MODE)
            except OSError as failure:
                raise SceneAssetMissingError(
                    f"image '{reference}' could not be opened"
                ) from failure
        return self._images[reference]
