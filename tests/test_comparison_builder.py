from pandas.testing import assert_frame_equal

from tests.conftest import make_analysis
from lifecycle.comparison_builder import ComparisonBuilder

def test_overlap(sample_presence):

    left = make_analysis(
        sample_presence,
        name="LEFT",
        columns=["NORMAL"],
    )

    right = make_analysis(
        sample_presence,
        name="RIGHT",
        columns=["NORMAL"],
    )

    comparison = ComparisonBuilder.from_analysis(
        left,
        right,
    )

    expected = (
        left.activity.lifetime &
        right.activity.lifetime
    )

    assert_frame_equal(
        comparison.overlap,
        expected,
    )


def test_no_overlap(sample_presence):

    left = make_analysis(
        sample_presence,
        name="LEFT",
        columns=["NORMAL"],
    )

    right = make_analysis(
        sample_presence,
        name="RIGHT",
        columns=["NEVER"],
    )

    comparison = ComparisonBuilder.from_analysis(
        left,
        right,
    )

    expected = (
        left.activity.lifetime &
        right.activity.lifetime
    )

    assert_frame_equal(
        comparison.overlap,
        expected,
    )