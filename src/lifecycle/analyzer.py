from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import numpy as np

from .analysis_data_builder import AnalysisData

class LifecycleAnalyzer:
    def __init__(self, analysis_data: AnalysisData):

        self.analysis_data = analysis_data
        self.activity = analysis_data.activity


    # test OK
    def duration(self) -> pd.Series:

        samples = self.activity.lifetime.sum()

        seconds = samples * self.analysis_data.sample_interval

        return pd.to_timedelta(seconds, unit="s")

    # test OK
    def segment_duration(self) -> pd.Series:
        """
        Duration of each segment.

        Index:
            lifecycle, segment_id
        """

        return pd.to_timedelta(
            self.activity.segment_length
             * self.analysis_data.sample_interval,
            unit="s",
        )

    def _segment_duration_samples(self) -> pd.Series:

        return self.activity.segment_length.astype(
            "int32"
        )
    
    # test OK
    def mean_segment_duration(self):

        return (
            self.segment_duration()
            .groupby(level=0)
            .mean()
        )

    # test OK
    def max_segment_duration(self):

        return (
            self.segment_duration()
            .groupby(level=0)
            .max()
        )

    # test OK
    def min_segment_duration(self):

        return (
            self.segment_duration()
            .groupby(level=0)
            .min()
        )



    def mean_segment_duration_seconds(self) -> pd.Series:
        """
        Mean segment duration in seconds.
        """

        return (
            self._segment_duration_samples()
            .groupby(level=0)
            .mean()
            * self.analysis_data.sample_interval
        )


    def max_segment_duration_seconds(self) -> pd.Series:
    
        return (
            self._segment_duration_samples()
            .groupby(level=0)
            .max()
            * self.analysis_data.sample_interval
        )


    def min_segment_duration_seconds(self) -> pd.Series:

        return (
            self._segment_duration_samples()
            .groupby(level=0)
            .min()
            * self.analysis_data.sample_interval
        )


    def segment_count(self) -> pd.Series:
        count = (
            self.activity
            .segment_length
            .groupby(level=0)
            .count()
        )

        return count.reindex(
            self.activity
            .lifetime.columns,
            fill_value=0,
        )

    '''
    def age(self, now=None):
        """
        analysis開始から現在までの経過時間
        """
        pass


    def active(self, now=None):
        """
        現在も生存しているか
        """
        return self.analysis_data.end is None


    def inactive(self, now=None):
        """
        終了済みか
        """
        return not self.active()
    '''
    
    def active_duration(self) -> pd.Series:
        return (
            self.activity.segment_length
            .groupby(level=0)
            .max()
        )


    # ==========================================================
    # Distribution
    # ==========================================================

    def lifetime_distribution(self) -> pd.Series:
        """
        Distribution of lifecycle duration.

        Returns
        -------
        pd.Series
            index:
                lifecycle id
            value:
                duration
        """

        return self.duration()


    def segment_distribution(self) -> pd.Series:
        """
        Distribution of segment duration.

        Returns
        -------
        pd.Series
            index:
                (lifecycle id, segment id)
            value:
                segment duration
        """

        return self.segment_duration()


    # ==========================================================
    # Structure
    # ==========================================================

    def samples(self) -> pd.Series:
        return (
            self.activity
            .lifetime.sum(axis=0)
        )
    
    def segments(self) -> pd.Series:
        return (
            self.activity
            .boundary
            .boundary_start
            .sum(axis=0)
        )

    # ==========================================================
    # Quality
    # ==========================================================

    def duplicate(self) -> pd.Series:
        return self.analysis_data.quality.duplicate.any(axis=0)

    def orphan(self) -> pd.Series:
        return self.analysis_data.quality.orphan.any(axis=0)

    def good(self) -> pd.Series:
        return self.analysis_data.quality.good.all(axis=0)

    def started_before(self) -> pd.Series:
        """
        Lifecycle started before observation window.
        """

        mask = self.analysis_data.analysis_mask

        return ~mask.iloc[0]

    def ended_after(self) -> pd.Series:
        """
        Lifecycle continued after observation window.
        """

        mask = self.analysis_data.analysis_mask

        return ~mask.iloc[-1]

    def complete(self) -> pd.Series:
        return (
            ~self.started_before()
            &
            ~self.ended_after()
        )

    def coverage_ratio(self) -> pd.Series:
        """
        Fraction of active samples retained for analysis.
        """

        raw_samples = self.analysis_data.raw_state.sum(axis=0)

        analysis_samples = (
            self.analysis_data.analysis_state
            .sum(axis=0)
        )

        return (
            analysis_samples
            / raw_samples.replace(0, pd.NA)
        )


    # test OK
    # ==========================================================
    # Summary
    # ==========================================================
    def summary(self) -> pd.DataFrame:
        """
        One row per lifecycle.
        """

        return pd.DataFrame(
            {
                # Time
                "duration": self.duration(),
                "active_duration": self.active_duration(),

                # Structure
                "samples": self.samples(),
                "segments": self.segments(),
                "segment_count": self.segment_count(),
                "coverage_ratio" : self.coverage_ratio(),

                # segments
                "mean_segment_duration": self.mean_segment_duration(),
                "max_segment_duration": self.max_segment_duration(),
                "min_segment_duration": self.min_segment_duration(),

                # Quality
                "duplicate": self.duplicate(),
                "orphan": self.orphan(),
                "good": self.good(),
                "started_before": self.started_before(),
                "ended_after": self.ended_after(),
                "complete": self.complete(),

            }
        )


    # test OK
    def statistics(self) -> pd.DataFrame:
        """
        analysis特徴量の統計情報
        """

        summary = self.summary()

        df = summary.copy()

        df["duration"] = (
            df["duration"]
            .dt.total_seconds()
        )

        numeric = df.select_dtypes(
            include="number"
        )

        return numeric.describe()


    # test OK
    def histogram(
        self,
        column: str,
        bins: int | None = None,
    ):
        """
        analysis Feature のヒストグラム用データ

        Parameters
        ----------
        column:
            summary() の列名

        bins:
            ヒストグラム分割数

        Returns
        -------
        counts, bins
        """

        summary = self.summary()

        if column not in summary.columns:
            raise ValueError(
                f"Unknown feature: {column}"
            )


        data = summary[column]


        #
        # Timedelta対応
        #
        if pd.api.types.is_timedelta64_dtype(data):
            data = data.dt.total_seconds()


        #
        # bool除外
        #
        if data.dtype == bool:
            raise TypeError(
                "Boolean feature cannot make histogram"
            )


        counts, edges = np.histogram(
            data.dropna(),
            bins=bins,
        )

        return pd.DataFrame(
            {
                "count": counts,
                "left": edges[:-1],
                "right": edges[1:],
            }
        )
    
