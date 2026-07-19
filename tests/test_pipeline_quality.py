import pandas as pd

from lifecycle.pipelines.quality import (
    _quality_from_state,
)

#
# tests _quality_from_state
#

def test_quality_from_state():

    state = pd.DataFrame(
        {
            "A": [0, 1, 2, 1, 0],
            "B": [0, 1, 1, -1, 0],
            "C": [0, 1, 1, 1, 0],
        },
        index=pd.date_range(
            "2026-01-01",
            periods=5,
            freq="min",
        ),
    )

    quality = _quality_from_state(state)

    assert quality.duplicate.loc[
        "2026-01-01 00:02:00",
        "A",
    ]

    assert quality.orphan.loc[
        "2026-01-01 00:03:00",
        "B",
    ]

    assert quality.good.loc[
        "2026-01-01 00:01:00",
        "C",
    ]

