import pandas as pd
import dataclasses
import pytest

from .asserts import assert_observation_equal

from lifecycle.builder import LifecycleBuilder
from lifecycle.pipelines.presence import (
    _presence_from_events,
    _presence_resample,
    _transition_from_presence,
    _state_from_transition,
    _observation_from_presence
)

#
# tests for Lifecycle Builder
#

def test_from_presence_name1():

    presence = pd.DataFrame(
        {
            "present": [False, True, True, False],
        },
        index=pd.to_datetime(
            [
                "2026-01-01 00:00:00",
                "2026-01-01 00:01:00",
                "2026-01-01 00:02:00",
                "2026-01-01 00:03:00",
            ]
        ),
    )

    lifecycle = LifecycleBuilder.from_presence(
        presence,
        name="ASSURED",
    )

    assert lifecycle.name == "ASSURED"

def test_from_events_default_name(sample_events):

    lifecycle = LifecycleBuilder.from_events(
        sample_events,
        event="ASSURED",
    )

    assert lifecycle.name == "ASSURED"

def test_from_events_custom_name(sample_events):

    lifecycle = LifecycleBuilder.from_events(
        sample_events,
        event="ASSURED",
        name="CUSTOM",
    )

    assert lifecycle.name == "CUSTOM"

def test_from_events_presence(sample_events):

    lifecycle = LifecycleBuilder.from_events(
        sample_events,
        event="ASSURED",
    )

    expected = _presence_from_events(
        sample_events,
        event="ASSURED",
    )

    pd.testing.assert_frame_equal(
        lifecycle.presence,
        expected,
    )

def test_from_events_interval(sample_events):

    lifecycle = LifecycleBuilder.from_events(
        sample_events,
        event="ASSURED",
        interval="2min",
    )

    expected = _presence_from_events(
        sample_events,
        event="ASSURED",
    )

    expected = _presence_resample(
        expected,
        interval="2min",
    )

    pd.testing.assert_frame_equal(
        lifecycle.presence,
        expected,
    )


def test_from_presence_presence(sample_presence):

    lifecycle = LifecycleBuilder.from_presence(
        sample_presence,
        name="TEST",
    )

    pd.testing.assert_frame_equal(
        lifecycle.presence,
        sample_presence,
    )


def test_from_presence_lifecycle(sample_presence):

    lifecycle = LifecycleBuilder.from_presence(
        sample_presence,
        name="TEST",
    )

    expected_transition = _transition_from_presence(
        sample_presence,
    )

    pd.testing.assert_frame_equal(
        lifecycle.transition,
        expected_transition,
    )

    expected_state = _state_from_transition(
        expected_transition,
    )

    pd.testing.assert_frame_equal(
        lifecycle.state,
        expected_state,
    )

    expected_observation = _observation_from_presence(
        sample_presence,
    )

    assert_observation_equal(
        lifecycle.observation,
        expected_observation,
    )

def test_lifecycle_frozen(sample_presence):

    lifecycle = LifecycleBuilder.from_presence(
        sample_presence,
        name="TEST",
    )

    with pytest.raises(
        dataclasses.FrozenInstanceError
    ):
        lifecycle.name = "CHANGE"

def test_builder_pipeline_consistency(sample_presence):

    lifecycle = LifecycleBuilder.from_presence(
        sample_presence,
        name="TEST",
    )

    transition = _transition_from_presence(
        sample_presence,
    )

    assert lifecycle.transition.equals(
        transition
    )

    state = _state_from_transition(
        transition,
    )

    assert lifecycle.state.equals(
        state,
    )

