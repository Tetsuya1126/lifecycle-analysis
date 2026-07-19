import pandas as pd
import numpy as np

from ..model import (
    BoundaryMask,
    ActivityAnalysis,
)

#
# active
#
def _find_active(state):
    #
    # Active
    #
    active = state > 0

    prev = active.shift(
        fill_value=False,
    )

    return active, prev

#
# boundry
#
def _find_boundary(active, prev):
    boundary_start = (
        ~prev
        & active
    )

    boundary_end = (
        prev
        & ~active
    )

    return BoundaryMask(
        boundary_start=boundary_start,
        boundary_end=boundary_end,
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


def _build_segment_series(
    lifecycle: list,
    segment: list,
    lengths: list,
) -> pd.Series:
    """
    MultiIndex Seriesへ変換
    """

    index = pd.MultiIndex.from_arrays(
        [
            lifecycle,
            segment,
        ],
        names=[
            "lifecycle",
            "segment",
        ],
    )

    return pd.Series(
        lengths,
        index=index,
        dtype="int16",
    )


def _segment_length_from_boundary(
    boundary: BoundaryMask,
) -> pd.Series:
    """
    BoundaryからSegment Lengthを計算

    Returns
    -------
    MultiIndex Series
        index = (lifecycle, segment)
        value = segment length
    """
    boundary_start = boundary.boundary_start
    boundary_end = boundary.boundary_end
    
    lifecycle = []
    segment = []
    lengths = []

    n_rows = len(boundary_start)

    for col in boundary_start.columns:

        start, end = _segment_position(
            boundary_start[col],
            boundary_end[col],
        )

        seg_length = _segment_lengths(
            start,
            end,
            n_rows,
        )

        _append_segments(
            lifecycle=lifecycle,
            segment=segment,
            lengths=lengths,
            name=col,
            seg_length=seg_length,
        )

    return _build_segment_series(
        lifecycle=lifecycle,
        segment=segment,
        lengths=lengths,
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

    #
    # Active
    #
    active, prev = _find_active(state)
    
    #
    # Boundary
    #
    boundary = _find_boundary(active, prev)

    #
    # segment_length
    #
    segment_length = _segment_length_from_boundary(
        boundary,
    )

    return ActivityAnalysis(
        lifetime=active,
        boundary=boundary,
        segment_length=segment_length,
    )


