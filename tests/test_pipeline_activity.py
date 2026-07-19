import numpy as np
import pandas as pd
import pandas.testing as pdt

from lifecycle.pipelines.presence import (
    _transition_from_presence,
    _state_from_transition,
)

from lifecycle.pipelines.activity import (
#    _lifetime_from_state,
#    _boundary_from_state,
    _activity_from_state,
)

#
# tests for _activity_from_state
#

def test_state_equals_presence(sample_presence):

    presence = sample_presence

    transition = _transition_from_presence(presence)
    state = _state_from_transition(transition)
    lifetime = _activity_from_state(state).lifetime

    pdt.assert_frame_equal(
        lifetime,
        presence,
    )


def test_lifetime(sample_presence):

    presence = sample_presence

    transition = _transition_from_presence(presence)
    state = _state_from_transition(transition)
    lifetime = _activity_from_state(state).lifetime

    pdt.assert_frame_equal(lifetime, presence)



def test_lifetime_equals_state_gt_zero(sample_presence):

    transition = _transition_from_presence(
        sample_presence
    )

    state = _state_from_transition(
        transition
    )

    lifetime = _activity_from_state(state).lifetime

    expected = state.gt(0)

    pdt.assert_frame_equal(
        lifetime,
        expected,
    )


def test_boundary_from_state(sample_presence):

    transition = _transition_from_presence(
        sample_presence,
    )

    state = _state_from_transition(
        transition,
    )

    boundary = _activity_from_state(state).boundary

    # ==========================================================
    # NORMAL
    # False False True True True False False False
    #
    # start : index 2
    # end   : index 5
    # duration : 1,2,3
    # ==========================================================

    assert boundary.boundary_start.loc[
        sample_presence.index[2],
        "NORMAL",
    ]

    assert boundary.boundary_end.loc[
        sample_presence.index[5],
        "NORMAL",
    ]


    # ==========================================================
    # SPLIT
    # False True True False False True True False
    #
    # lifecycleが2回
    # ==========================================================

    assert list(
        boundary.boundary_start["SPLIT"]
    ) == [
        False, True, False, False,
        False, True, False, False,
    ]

    assert list(
        boundary.boundary_end["SPLIT"]
    ) == [
        False, False, False, True,
        False, False, False, True,
    ]


    # ==========================================================
    # NEVER
    # 全期間 inactive
    # ==========================================================

    assert not boundary.boundary_start["NEVER"].any()
    assert not boundary.boundary_end["NEVER"].any()




'''
'''
def test_segment_id(sample_lifecycle):

    state = sample_lifecycle.state

    activity = _activity_from_state(state)

    segment = activity.segment_length

    # NORMAL
    assert segment["NORMAL"].index.max() == 1

    # SPLIT
    assert segment["SPLIT"].index.max() == 2

    # PULSE
    assert segment["PULSE"].index.max() == 1

    # PULSE2
    assert segment["PULSE2"].index.max() == 2

    # NEVER
    assert segment.get("NEVER", 0) == 0

    # GAP
    assert segment["GAP"].index.max() == 2

    # ZIGZAG
    assert segment["ZIGZAG"].index.max() == 4


def test_segment_length(sample_lifecycle):

    state = sample_lifecycle.state

    activity = _activity_from_state(state)

    length = activity.segment_length

#    length = _segment_length(segment)

    #
    # NORMAL
    #
    assert length.loc[("NORMAL", 1)] == 3

    #
    # SPLIT
    #
    assert length.loc[("SPLIT", 1)] == 2
    assert length.loc[("SPLIT", 2)] == 2

    #
    # PULSE
    #
    assert length.loc[("PULSE", 1)] == 1

    #
    # PULSE2
    #
    assert length.loc[("PULSE2", 1)] == 3
    assert length.loc[("PULSE2", 2)] == 2

    #
    # NEVER
    #
    assert "NEVER" not in length.index.get_level_values(0)

    #
    # GAP
    #
    assert length.loc[("GAP", 1)] == 4
    assert length.loc[("GAP", 2)] == 3

    #
    # EDGE_START
    #
    assert length.loc[("EDGE_START", 1)] == 1

    #
    # EDGE_END
    #
    assert length.loc[("EDGE_END", 1)] == 1

    #
    # EDGE_BOTH
    #
    assert length.loc[("EDGE_BOTH", 1)] == 1
    assert length.loc[("EDGE_BOTH", 2)] == 1

    #
    # ZIGZAG
    #
    assert length.loc[("ZIGZAG", 1)] == 1
    assert length.loc[("ZIGZAG", 2)] == 1
    assert length.loc[("ZIGZAG", 3)] == 1
    assert length.loc[("ZIGZAG", 4)] == 1
'''
'''
