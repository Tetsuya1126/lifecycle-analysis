import pandas as pd
import numpy as np

from ..model import (
    QualityMask,
)

from .pandas_converter import (
    to_array,
    to_df,
    to_series,
)

# test OK
def _quality_from_state(
    state: pd.DataFrame,
) -> QualityMask:
    """
    State -> Quality
    """
    arr = to_array(state, np.int8)

    duplicate = arr > 1
    orphan = arr < 0
    good = (arr >= 0) & (arr <= 1)

    return QualityMask(
        duplicate=to_df(duplicate, state),
        orphan=to_df(orphan, state),
        good=to_df(good, state),
    )