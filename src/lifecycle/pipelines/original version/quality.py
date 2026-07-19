import pandas as pd


from ..model import (
    QualityMask,
)


# test OK
def _quality_from_state(
    state: pd.DataFrame,
) -> QualityMask:
    """
    State -> Quality
    """

    duplicate = state > 1

    orphan = state < 0

    good = (
        (state == 0)
        | (state == 1)
    )

    return QualityMask(
        duplicate=duplicate,
        orphan=orphan,
        good=good,
    )

