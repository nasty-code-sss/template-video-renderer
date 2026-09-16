import pytest

from template_video_renderer.domain.video.entity.scene import Scene
from template_video_renderer.domain.video.entity.video_project import VideoProject
from template_video_renderer.domain.video.error.empty_project_error import EmptyProjectError
from template_video_renderer.domain.video.error.invalid_timing_error import InvalidTimingError
from template_video_renderer.domain.video.policy.scene_timeline import SceneTimeline
from template_video_renderer.domain.video.value.frame_rate import FrameRate
from template_video_renderer.domain.video.value.timing_spec import TimingSpec

FRAME_RATE = FrameRate(frames_per_second=30)
TIMING = TimingSpec(
    scene_seconds=4.0,
    transition_seconds=1.0,
    title_delay_seconds=0.5,
    subtitle_delay_seconds=1.0,
    text_fade_seconds=0.5,
)


def project_with(scene_count: int) -> VideoProject:
    scenes = tuple(
        Scene(title=f"title {number}", subtitle=f"subtitle {number}", image_reference=None)
        for number in range(scene_count)
    )
    return VideoProject(name="test", scenes=scenes, audio_reference=None)


def timeline_for(scene_count: int) -> SceneTimeline:
    return SceneTimeline(project_with(scene_count), TIMING, FRAME_RATE)


def test_total_seconds_for_single_scene_equals_scene_duration() -> None:
    assert timeline_for(1).total_seconds == pytest.approx(4.0)


def test_total_seconds_subtracts_overlap_of_every_transition() -> None:
    assert timeline_for(3).total_seconds == pytest.approx(10.0)


def test_total_frames_matches_duration_at_given_frame_rate() -> None:
    assert timeline_for(3).total_frames == 300


def test_first_frame_shows_only_first_scene() -> None:
    plan = timeline_for(3).plan_frame(0)

    assert [layer.scene_index for layer in plan.layers] == [0]
    assert plan.is_transition is False


def test_frame_inside_transition_shows_both_scenes() -> None:
    plan = timeline_for(2).plan_frame(FRAME_RATE.frames_in(3.5))

    assert [layer.scene_index for layer in plan.layers] == [0, 1]
    assert plan.is_transition is True


def test_incoming_scene_is_half_visible_in_the_middle_of_transition() -> None:
    plan = timeline_for(2).plan_frame(FRAME_RATE.frames_in(3.5))

    incoming = plan.layers[1]
    assert incoming.scene_opacity.value == pytest.approx(0.5)


def test_incoming_scene_is_fully_visible_when_transition_ends() -> None:
    plan = timeline_for(2).plan_frame(FRAME_RATE.frames_in(4.0))

    assert plan.layers[0].scene_index == 1
    assert plan.layers[0].scene_opacity.value == pytest.approx(1.0)


def test_title_stays_invisible_until_its_delay_passes() -> None:
    plan = timeline_for(1).plan_frame(FRAME_RATE.frames_in(0.4))

    assert plan.layers[0].title_opacity.is_invisible is True


def test_title_reaches_full_opacity_after_fade_completes() -> None:
    plan = timeline_for(1).plan_frame(FRAME_RATE.frames_in(1.0))

    assert plan.layers[0].title_opacity.value == pytest.approx(1.0)


def test_accent_bar_is_complete_at_the_end_of_the_scene() -> None:
    plan = timeline_for(1).plan_frame(FRAME_RATE.frames_in(3.9))

    assert plan.layers[0].accent_progress == pytest.approx(1.0, abs=0.05)


def test_every_planned_frame_has_at_least_one_visible_scene() -> None:
    timeline = timeline_for(4)

    assert all(plan.layers for plan in timeline.plan_frames())


def test_planned_frame_count_matches_total_frames() -> None:
    timeline = timeline_for(2)

    assert len(list(timeline.plan_frames())) == timeline.total_frames


def test_project_without_scenes_is_rejected() -> None:
    with pytest.raises(EmptyProjectError):
        VideoProject(name="empty", scenes=(), audio_reference=None)


def test_transition_longer_than_scene_is_rejected() -> None:
    with pytest.raises(InvalidTimingError):
        TimingSpec(
            scene_seconds=1.0,
            transition_seconds=2.0,
            title_delay_seconds=0.0,
            subtitle_delay_seconds=0.0,
            text_fade_seconds=0.5,
        )
