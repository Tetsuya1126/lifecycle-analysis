
#import cProfile, pstats
import numpy as np
import pandas as pd

from lifecycle import LifecycleAnalysis

#pr = cProfile.Profile()


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

#pr.enable()

analysis = LifecycleAnalysis(
    df = event_df,
    event = event_name,
    trusted = True,
)

#pr.disable()

df = analysis.summary()
    
print(df)
    
#stats = pstats.Stats(pr)
#stats.sort_stats("cumulative")
#stats.print_stats(30)

