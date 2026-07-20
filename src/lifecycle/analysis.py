import pandas as pd

from .builder import LifecycleBuilder
from .analysis_data_builder import AnalysisBuilder
from .analyzer import LifecycleAnalyzer


class LifecycleAnalysis:
    """
    Public interface for lifecycle analysis.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        *,
        event: str,
        trusted: bool = True,
        name: str | None = None,
        event_col: str = "event",
        time_col: str = "datetime",
        ip_col: str = "ip",
        interval: str | None = None,
    ):

        lifecycle = LifecycleBuilder.from_events(
            df,
            event=event,
            name=name,
            event_col=event_col,
            time_col=time_col,
            ip_col=ip_col,
            interval=interval,
        )

        analysis = AnalysisBuilder.from_lifecycle(
            lifecycle,
            trusted=trusted,
        )

        self.analyzer = LifecycleAnalyzer(
            analysis
        )


    def summary(self) -> pd.DataFrame:
        return self.analyzer.summary()


    def statistics(self) -> pd.DataFrame:
        return self.analyzer.statistics()


    def histogram(
        self,
        column: str,
        bins: int | None = None,
    ):
        return self.analyzer.histogram(
            column,
            bins=bins,
        )
