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

if __name__ == "__main__":

#    import cProfile, pstats
    import numpy as np
    import pandas as pd
    
#    pr = cProfile.Profile()


    N = 100_000

    rng = np.random.default_rng(42)

    event_df = pd.DataFrame(
        {
            "ip": rng.choice(
                [f"192.0.2.{i}" for i in range(1, 1001)],
                size=N,
            ),
            "event": rng.choice(
                [
                    "ASSURED",
                    "INVALID_SNI",
                    "ISOLATE",
                    "TIMEOUT",
                ],
                size=N,
                p=[0.7, 0.1, 0.1, 0.1],
            ),
            "datetime": pd.Timestamp("2026-01-01")
            + pd.to_timedelta(
                np.sort(rng.integers(0, 86400, size=N)),
                unit="s",
            ),
        }
    )

    event_name = "ASSURED"

#    pr.enable()

    analysis = LifecycleAnalysis(
        df = event_df,
        event = event_name,
        trusted = True,
    )

#    pr.disable()

    df = analysis.summary()
    
    print(df)
    
#    stats = pstats.Stats(pr)
#    stats.sort_stats("cumulative")
#    stats.print_stats(30)

