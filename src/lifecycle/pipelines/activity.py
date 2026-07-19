import pandas as pd
import numpy as np

from ..model import (
    BoundaryMask,
    ActivityAnalysis,
)

from .pandas_converter import (
    to_array,
    to_df,
    to_series,
    to_pandas,
)

#
# active
#
def _find_active(state):
    #
    # Active
    #
    active = state > 0

    prev = np.empty_like(active)
    prev[0] = False
    prev[1:] = active[:-1]

    return active, prev

#
# boundry
#
def __find_boundary(active, prev):
    boundary_start = (
        ~prev
        & active
    )

    boundary_end = (
        prev
        & ~active
    )

    return (
        boundary_start,
        boundary_end,
    )

def _find_boundary(active, prev):
    return (
        active & ~prev,
        prev & ~active,
    )

#
# segment length
#
def _segment_position(
    boundary_start: pd.Series,
    boundary_end: pd.Series,
) -> tuple[np.ndarray, np.ndarray]:
    """
    1列分のSegment開始・終了位置を取得
    """

    start = np.flatnonzero(boundary_start.to_numpy())
    end = np.flatnonzero(boundary_end.to_numpy())

    return start, end


def _segment_lengths(
    start: np.ndarray,
    end: np.ndarray,
    n_rows: int,
) -> np.ndarray:
    """
    開始・終了位置からSegment長を計算
    """

    # 最後まで継続しているSegment
    if len(start) > len(end):
        end = np.append(end, n_rows)

    return end - start


def _append_segments(
    lifecycle: list,
    segment: list,
    lengths: list,
    name: str,
    seg_length: np.ndarray,
) -> None:
    """
    Segment情報を蓄積
    """

    n = len(seg_length)

    if n == 0:
        return

    lifecycle.extend(
        [name] * n
    )

    segment.extend(
        range(1, n + 1)
    )

    lengths.extend(
        seg_length.tolist()
    )


def _segment_length_from_boundary(
    boundary_start: np.ndarray,
    boundary_end: np.ndarray,
    like: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:

    lifecycle = []
    segment = []
    lengths = []

    n_rows = boundary_start.shape[0]

    for i, name in enumerate(like.columns):

        start = np.flatnonzero(boundary_start[:, i])
        end = np.flatnonzero(boundary_end[:, i])

        seg_length = _segment_lengths(
            start,
            end,
            n_rows,
        )

        _append_segments(
            lifecycle=lifecycle,
            segment=segment,
            lengths=lengths,
            name=name,
            seg_length=seg_length,
        )

    return (
        np.asarray(lifecycle, dtype=object),
        np.asarray(segment, dtype=np.int16),
        np.asarray(lengths, dtype=np.int16),
    )

def _activity_from_state(
    state: pd.DataFrame,
) -> ActivityAnalysis:
    """
    State -> ActivityAnalysis

    導出される情報

        lifetime
        boundary_start
        boundary_end
        segment_length
    """
    state_array = to_array(state)
    #
    # Active
    #
    active, prev = _find_active(state_array)

    #
    # Boundary array
    #
    boundary_start, boundary_end = _find_boundary(active, prev)

    #
    # segment_length
    #
    lifecycle, segment, lengths = _segment_length_from_boundary(
        boundary_start,
        boundary_end,
        state,
    )


    return ActivityAnalysis(
        lifetime = to_df(active, state),
        boundary = BoundaryMask(
            boundary_start=to_df(boundary_start, state),
            boundary_end=to_df(boundary_end, state),
        ),
        segment_length = pd.Series(
            lengths,
            index = pd.MultiIndex.from_arrays(
                [lifecycle, segment],
                names=["lifecycle", "segment"],
            ),
            dtype = "int16",
        ),
    )


