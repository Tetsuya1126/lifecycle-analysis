import pandas as pd
from dataclasses import dataclass
from typing import (
    Dict,
)

@dataclass(slots=True, frozen=True)
class BoundaryMask:
    # 状態変化点情報
    boundary_start: pd.DataFrame
    boundary_end: pd.DataFrame


@dataclass(slots=True, frozen=True)
class QualityMask:
    duplicate: pd.DataFrame
    orphan: pd.DataFrame
    good: pd.DataFrame


@dataclass(slots=True, frozen=True)
class ObservationMask:
    observed: pd.Series

    # IP単位の要約情報
    started_before: pd.Series
    ended_after: pd.Series
    complete: pd.Series

    # 時系列 × IP の解析用Mask
    #  -> 中途半端なレコードを削除するMASK
    trusted_mask: pd.DataFrame


@dataclass(slots=True, frozen=True)
class Lifecycle:

    name: str

    presence: pd.DataFrame
    transition: pd.DataFrame
    state: pd.DataFrame

    observation: ObservationMask

    sample_interval: int = 60



@dataclass(slots=True, frozen=True)
class ActivityAnalysis:

    lifetime: pd.DataFrame

    boundary: BoundaryMask

    segment_length: pd.Series


@dataclass(slots=True, frozen=True)
class AnalysisData:

    name: str

    #
    # Raw Data
    #
    raw_state: pd.DataFrame
    sample_interval: int
    quality: QualityMask

    #
    # Analysis Filter
    #
    analysis_mask: pd.DataFrame
    analysis_state: pd.DataFrame

    #
    # Activity Derived Analysis
    #
    activity : ActivityAnalysis

    



@dataclass(slots=True, frozen=True)
class LifecycleComparison:
    left_name: str
    right_name: str

    overlap: pd.DataFrame
    only_left: pd.DataFrame
    only_right: pd.DataFrame
    union: pd.DataFrame


'''
@dataclass(slots=True, frozen=True)
class LifecycleCollection:
    lifecycles: dict[str, Lifecycle]
'''



    
