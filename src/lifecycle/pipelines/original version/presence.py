import pandas as pd
import numpy as np

from ..model import (
    ObservationMask,
)


# test OK
def _presence_from_events(
    df: pd.DataFrame,
    *,
    event: str,
    time_col: str = "datetime",
    ip_col: str = "ip",
    event_col: str = "event",
) -> pd.DataFrame:
    """
    Event DataFrame → Presence(bool)

    指定したイベント名の Presence Mask を作成する。

    Parameters
    ----------
    df : pd.DataFrame
        元データ

    name : str
        イベント名
        例:
            "ASSURED"
            "SYN_RECV"
            "INVALID_CLIENTHELLO"
            "isolate"

    event_col : str
        イベント名の列

    time_col : str
        時刻列

    ip_col : str
        IP列

    Returns
    -------
    pd.DataFrame
        index   : datetime
        columns : ip
        values  : bool

        
    """

    return (
        df.loc[df[event_col] == event]
        .assign(present=True)
        .pivot_table(
            index=time_col,
            columns=ip_col,
            values="present",
            aggfunc="any",
            fill_value=False,
        )
        .astype(bool)
        .sort_index()
    )

# test OK
def _presence_resample(
    presence: pd.DataFrame,
    *,
    interval: str,
) -> pd.DataFrame:
    """
    Presenceを指定間隔へリサンプリングする。

    Parameters
    ----------
    presence
        Presence(bool) DataFrame

    interval
        pandas offset alias
        例: "30s", "1min", "5min"

    Returns
    -------
    pd.DataFrame
        Resampled Presence(bool)
    """

    if not isinstance(presence.index, pd.DatetimeIndex):
        raise TypeError(
            "presence.index must be DatetimeIndex"
        )

    return (
        presence
        .resample(interval)
        .max()
        .fillna(False)
        .astype(bool)
    )

# test OK
def _transition_from_presence(
    presence: pd.DataFrame,
) -> pd.DataFrame:
    """
    Presence(bool) → Transition(int8)

    Transition
        +1 : IN
         0 : No change
        -1 : OUT
    """
    previous = presence.shift(
        periods=1,
        fill_value=False,
    )

    transition = (
        presence.astype("int8")
        - previous.astype("int8")
    )

    return transition.astype("int8")



def _valid_mask(
    seen_start,
    seen_end,
    observed
):
    #
    # vaild mask
    #
    valid_mask = (
        seen_start
        &
        seen_end
    )

    valid_mask = (
        valid_mask
        & observed.reindex(valid_mask.columns)
    )

    return valid_mask


def _find_edge_observation_both_side(
    active
):
    '''
    inactive.cumsum() > 0 より .cummax()の方が早い
    '''
    inactive = ~active

    # 左側:
    # 最初のOFFを見るまで無効
    #
    seen_start = inactive.cummax()

    #
    # 右側:
    # 最後のOFF以降を無効
    #
    seen_end = (
        inactive.iloc[::-1]
                .cummax()
                .iloc[::-1]
    )

    return seen_start, seen_end


def _find_boundary_each_ip(
    active, presence
):
    #
    # IP単位の境界判定
    #

    started_before = (
        active.iloc[0]
    )

    ended_after = (
        active.iloc[-1]
    )

    observed = presence.any()

    complete = (
        observed
        &
        ~started_before
        &
        ~ended_after
    )
    return started_before, ended_after, observed, complete


# test OK
def _observation_from_presence(
    presence: pd.DataFrame,
) -> ObservationMask:
    """
    Presence -> ObservationMask

    観測境界を判定する。

    started_before:
        観測開始時点ですでに存在していたIP

    ended_after:
        観測終了時点でも存在しているIP

    complete:
        開始・終了とも観測できたIP

    valid_mask:
        救出可能な解析範囲(time x IP)
    """

    active = presence.astype(bool)


    #
    # IP単位の境界判定
    #
    started_before, ended_after, observed, complete = _find_boundary_each_ip(
        active,
        presence
    )

    #
    # 時系列valid mask
    #
    seen_start, seen_end = _find_edge_observation_both_side(
        active
    )

    #
    # vaild mask
    #
    valid_mask = _valid_mask(
        seen_start,
        seen_end,
        observed
    )

    return ObservationMask(
        observed=observed,
        started_before=started_before,
        ended_after=ended_after,
        complete=complete,
        trusted_mask=valid_mask,
    )


# test OK
def _sample_interval(
    index: pd.DatetimeIndex,
) -> int:
    """
    DatetimeIndexからサンプリング周期(秒)を返す。
    """

    if len(index) < 2:
        raise ValueError(
            "Need at least two timestamps."
        )

    diff = index.to_series().diff().dropna()

    interval = diff.mode().iloc[0]

    return int(interval.total_seconds())


# test OK
def _state_from_transition(
    transition: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transition → State

    Stateは各時刻におけるライフサイクルの状態数を表す。

        0 : 不在
        1 : 存在
        2以上 : 異常（重複IN）
       -1以下 : 異常（OUT過多）
    """
    return transition.cumsum().astype("int8")
