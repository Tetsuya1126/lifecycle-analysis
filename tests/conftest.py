import pytest
import pandas as pd

'''
from lifecycle.model import Lifecycle

from lifecycle.pipelines.presence import (
    _presence_from_events,
    _transition_from_presence,
    _state_from_transition,
    _observation_from_presence,
    _presence_resample,
    _sample_interval,
)



from lifecycle.pipeline import (
    #_presence_from_events,
    #_transition_from_presence,
    #_state_from_transition,
    _lifetime_from_state,
    _boundary_from_state,
    _quality_from_state,
)
'''

from lifecycle.builder import LifecycleBuilder
from lifecycle.analysis_data_builder import AnalysisBuilder
from lifecycle.comparison_builder import ComparisonBuilder


# ==========================================================
# Test patterns for Lifecycle pipeline
#
# Each column represents one independent IP lifecycle.
#
# These patterns are shared by:
#   - Pipeline
#   - Builder
#   - Analyzer
# ==========================================================

@pytest.fixture
def sample_presence():

    index = pd.date_range(
        "2026-01-01",
        periods=8,
        freq="1min",
    )

    return pd.DataFrame(
{
    # ==========================================================
    # 1. Valid lifetime (解析対象)
    # ==========================================================

    "NORMAL": [False, False, True, True, True, False, False, False],     # 正常な1ライフタイム
    "SPLIT":  [False, True, True, False, False, True, True, False],      # 完全なライフタイムが2回
    "PULSE":  [False, False, False, True, False, False, False, False],   # 1サンプルのみ
    "PULSE2": [False, True, True, True, False, True, True, False],       # 1サンプル落ちてライフタイムが2回

    # ==========================================================
    # 2. No lifetime (解析対象外)
    # ==========================================================

    "NEVER":  [False, False, False, False, False, False, False, False],  # 一度も存在しない


    # ==========================================================
    # 3. Observation boundary (解析対象外)
    #    開始・終了が観測期間外
    # ==========================================================

    "STARTED_BEFORE": [True, True, True, False, False, False, False, False],
    "ENDED_AFTER":    [False, False, False, True, True, True, True, True],
    "ALWAYS":         [True, True, True, True, True, True, True, True],


    # ==========================================================
    # 4. Combination / Abnormal
    # ==========================================================

    "GAP":        [True, True, True, True, False, True, True, True],        # 内部欠落
    "EDGE_START": [True, False, False, False, False, False, False, False],  # 開始境界のみ
    "EDGE_END":   [False, False, False, False, False, False, False, True],  # 終了境界のみ
    "EDGE_BOTH":  [True, False, False, False, False, False, False, True],   # 両端境界
    "ZIGZAG":     [False, True, False, True, False, True, False, True],     # ON/OFF繰り返し
},
        index=index,
        dtype=bool,
    )


@pytest.fixture
def sample_events():

    return pd.DataFrame(
        {
            "ip": [
                "192.0.2.1",
                "192.0.2.2",
                "192.0.2.1",
                "192.0.2.3",
            ],
            "event": [
                "ASSURED",
                "ASSURED",
                "INVALID_SNI",
                "ASSURED",
            ],
            "datetime": pd.to_datetime(
                [
                    "2026-01-01 00:00:00",
                    "2026-01-01 00:01:00",
                    "2026-01-01 00:02:00",
                    "2026-01-01 00:03:00",
                ]
            ),
        }
    )


@pytest.fixture
def sample_lifecycle(sample_presence):
    """
    Standard Lifecycle fixture for analyzer tests.
    """
    return LifecycleBuilder.from_presence(
        sample_presence,
        name="sample",
    )



@pytest.fixture
def sample_analysis_data(sample_lifecycle):
    """
    Standard Lifecycle fixture for analyzer tests.
    """
    return AnalysisBuilder.from_lifecycle(
        sample_lifecycle,
        trusted=True
    )

@pytest.fixture
def sample_analysis_data_f(sample_lifecycle):
    """
    Standard Lifecycle fixture for analyzer tests.
    """
    return AnalysisBuilder.from_lifecycle(
        sample_lifecycle,
        trusted=False
    )



def make_analysis(
    sample_presence,
    *,
    name: str,
    columns: list[str],
):
    """
    sample_presenceからAnalysisDataを生成
    """

    lifecycle = LifecycleBuilder.from_presence(
        name=name,
        presence=(
            sample_presence[columns]
            .rename(columns=lambda _: "TARGET")
        ),
    )

    return AnalysisBuilder.from_lifecycle(
        lifecycle,
        trusted=True,
    )


