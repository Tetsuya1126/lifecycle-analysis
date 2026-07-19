import numpy as np
import pandas as pd
import pandas.testing as pdt

from lifecycle.pipelines.presence import (
    _transition_from_presence,
    _state_from_transition,
    _sample_interval,
    _observation_from_presence,
)

#
# tests for _pipeline_from_presence
#

#
# _sample_interval
#
def _sample_interval(
    index: pd.DatetimeIndex,
) -> int:
    """
    DatetimeIndexからサンプリング周期(秒)を返す。
    """

    if not isinstance(index, pd.DatetimeIndex):
        raise TypeError("index must be a pandas.DatetimeIndex")

    if len(index) < 2:
        raise ValueError(
            "Need at least two timestamps."
        )

    diff = index.to_series().diff().dropna()

    interval = diff.mode().iloc[0]

    return int(interval.total_seconds())


def test_sample_interval_datetime_index():
    index = pd.to_datetime(
        [
            "2026-01-01 00:00:00",
            "2026-01-01 00:01:00",
            "2026-01-01 00:02:00",
            "2026-01-01 00:03:00",
        ]
    )

    interval = _sample_interval(index)

    assert interval == 60


def test_sample_interval_regular():

    index = pd.to_datetime(
        [
            "2026-01-01 00:00:00",
            "2026-01-01 00:01:00",
            "2026-01-01 00:02:00",
            "2026-01-01 00:03:00",
        ]
    )

    assert _sample_interval(index) == 60


def test_sample_interval_mode():

    index = pd.to_datetime(
        [
            "2026-01-01 00:00:00",
            "2026-01-01 00:01:00",  # +60
            "2026-01-01 00:02:00",  # +60
            "2026-01-01 00:04:00",  # +120
            "2026-01-01 00:05:00",  # +60
        ]
    )

    assert _sample_interval(index) == 60

#
# test trnsition
#
def test_transition(sample_presence):

    transition = _transition_from_presence(
        sample_presence
    )

    expected = pd.DataFrame(
        {
            "NORMAL":         [ 0,  0,  1,  0,  0, -1,  0,  0],
            "SPLIT":          [ 0,  1,  0, -1,  0,  1,  0, -1],
            "PULSE":          [ 0,  0,  0,  1, -1,  0,  0,  0],
            "PULSE2":         [ 0,  1,  0,  0, -1,  1,  0, -1],

            "NEVER":          [ 0,  0,  0,  0,  0,  0,  0,  0],

            "STARTED_BEFORE": [ 1,  0,  0, -1,  0,  0,  0,  0],
            "ENDED_AFTER":    [ 0,  0,  0,  1,  0,  0,  0,  0],
            "ALWAYS":         [ 1,  0,  0,  0,  0,  0,  0,  0],

            "GAP":            [ 1,  0,  0,  0, -1,  1,  0,  0],
            "EDGE_START":     [ 1, -1,  0,  0,  0,  0,  0,  0],
            "EDGE_END":       [ 0,  0,  0,  0,  0,  0,  0,  1],
            "EDGE_BOTH":      [ 1, -1,  0,  0,  0,  0,  0,  1],
            "ZIGZAG":         [ 0,  1, -1,  1, -1,  1, -1,  1],
        },
        index=sample_presence.index,
        dtype=np.int8,
    )

#
# test state
#
def test_state(sample_presence):

    transition = _transition_from_presence(
        sample_presence
    )

    state = _state_from_transition(
        transition
    )

    expected = pd.DataFrame(
        {
            "NORMAL":         [0, 0, 1, 1, 1, 0, 0, 0],
            "SPLIT":          [0, 1, 1, 0, 0, 1, 1, 0],
            "PULSE":          [0, 0, 0, 1, 0, 0, 0, 0],
            "PULSE2":         [0, 1, 1, 1, 0, 1, 1, 0],

            "NEVER":          [0, 0, 0, 0, 0, 0, 0, 0],

            "STARTED_BEFORE": [1, 1, 1, 0, 0, 0, 0, 0],
            "ENDED_AFTER":    [0, 0, 0, 1, 1, 1, 1, 1],
            "ALWAYS":         [1, 1, 1, 1, 1, 1, 1, 1],

            "GAP":            [1, 1, 1, 1, 0, 1, 1, 1],
            "EDGE_START":     [1, 0, 0, 0, 0, 0, 0, 0],
            "EDGE_END":       [0, 0, 0, 0, 0, 0, 0, 1],
            "EDGE_BOTH":      [1, 0, 0, 0, 0, 0, 0, 1],
            "ZIGZAG":         [0, 1, 0, 1, 0, 1, 0, 1],
        },
        index=sample_presence.index,
        dtype=np.int8,
    )

    pdt.assert_frame_equal(
        state,
        expected,
    )

#
# tests state & transition
#
def test_transition_equals_state_diff(sample_presence):

    transition = _transition_from_presence(
        sample_presence
    )

    state = _state_from_transition(
        transition
    )

    reconstructed = (
        state.diff()
        .fillna(state.iloc[0])
        .astype(np.int8)
    )

    pdt.assert_frame_equal(
        transition,
        reconstructed,
    )

#
# test observation
#
def test_observation_from_presence(sample_presence):

    observation = _observation_from_presence(
        sample_presence,
    )


    # ==========================================================
    # NORMAL
    #
    # False False True True True False False False
    #
    # 完全観測
    # ==========================================================

    assert not observation.started_before["NORMAL"]

    assert not observation.ended_after["NORMAL"]

    assert observation.complete["NORMAL"]

    assert list(
        observation.trusted_mask["NORMAL"]
    ) == [
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
    ]

    assert observation.observed["NORMAL"]


    # ==========================================================
    # STARTED_BEFORE
    #
    # True True True False False False False False
    #
    # 開始前から存在
    # ==========================================================

    assert observation.started_before["STARTED_BEFORE"]

    assert not observation.ended_after["STARTED_BEFORE"]

    assert not observation.complete["STARTED_BEFORE"]

    assert list(
        observation.trusted_mask["STARTED_BEFORE"]
    ) == [
        False,
        False,
        False,
        True,
        True,
        True,
        True,
        True,
    ]


    # ==========================================================
    # ENDED_AFTER
    #
    # False False False True True True True True
    #
    # 終了点未観測
    # ==========================================================

    assert not observation.started_before["ENDED_AFTER"]

    assert observation.ended_after["ENDED_AFTER"]

    assert not observation.complete["ENDED_AFTER"]

    assert list(
        observation.trusted_mask["ENDED_AFTER"]
    ) == [
        True,
        True,
        True,
        False,
        False,
        False,
        False,
        False,
    ]


    # ==========================================================
    # ALWAYS
    #
    # True True True True...
    #
    # 完全なOFFがない
    # ==========================================================

    assert observation.started_before["ALWAYS"]

    assert observation.ended_after["ALWAYS"]

    assert not observation.complete["ALWAYS"]

    assert (
        observation.trusted_mask["ALWAYS"]
        == False
    ).all()



    # ==========================================================
    # NEVER
    #
    # 全期間OFF
    # ==========================================================

    assert not observation.started_before["NEVER"]

    assert not observation.ended_after["NEVER"]

    assert not observation.complete["NEVER"]

    assert (
        observation.trusted_mask["NEVER"]
        == False
    ).all()

    assert not observation.observed["NEVER"]

