import pandas as pd

from lifecycle.analysis_data_builder import (
    AnalysisBuilder,
)


import pandas as pd

from lifecycle.analysis_data_builder import AnalysisBuilder

#
# tests AnalysisBuilder
#

#
# tests AnalysisBuilder
#

def test_analysis_builder(sample_lifecycle):

    analysis = AnalysisBuilder.from_lifecycle(
        sample_lifecycle,
    )

    activity = analysis.activity

    #
    # Base
    #
    assert analysis.name == sample_lifecycle.name
    assert analysis.sample_interval == sample_lifecycle.sample_interval

    assert analysis.raw_state.shape == sample_lifecycle.transition.shape
    assert analysis.analysis_state.shape == sample_lifecycle.transition.shape
    assert analysis.analysis_mask.shape == sample_lifecycle.transition.shape

    #
    # Analysis Mask
    #
    assert analysis.analysis_mask["NORMAL"].all()
    assert not analysis.analysis_mask["ALWAYS"].any()

    #
    # Lifetime
    #
    assert activity.lifetime["NORMAL"].sum() == 3
    assert activity.lifetime["SPLIT"].sum() == 4

    #
    # Boundary
    #
    
    assert activity.boundary.boundary_start["NORMAL"].sum() == 1
    assert activity.boundary.boundary_end["NORMAL"].sum() == 1

    assert activity.boundary.boundary_start["SPLIT"].sum() == 2
    assert activity.boundary.boundary_end["SPLIT"].sum() == 2

    #
    # Segment
    #
    assert activity.segment_length.loc[("NORMAL", 1)] == 3
    assert activity.segment_length.loc[("SPLIT", 1)] == 2
    assert activity.segment_length.loc[("SPLIT", 2)] == 2


def test_analysis_builder_untrusted(sample_lifecycle):

    analysis = AnalysisBuilder.from_lifecycle(
        sample_lifecycle,
        trusted=False,
    )

    #
    # Maskは全部True
    #
    assert analysis.analysis_mask.all().all()

    #
    # StateはRawと一致
    #
    pd.testing.assert_frame_equal(
        analysis.analysis_state,
        analysis.raw_state,
    )
