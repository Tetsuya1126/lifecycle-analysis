import pandas as pd

def assert_observation_equal(actual, expected):

    pd.testing.assert_series_equal(
        actual.observed,
        expected.observed,
    )

    pd.testing.assert_series_equal(
        actual.started_before,
        expected.started_before,
    )

    pd.testing.assert_series_equal(
        actual.ended_after,
        expected.ended_after,
    )

    pd.testing.assert_series_equal(
        actual.complete,
        expected.complete,
    )

    pd.testing.assert_frame_equal(
        actual.trusted_mask,
        expected.trusted_mask,
    )