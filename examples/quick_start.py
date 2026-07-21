import pandas as pd
import numpy as np

from lifecycle import (
    LifecycleAnalysis,
)

def create_event(N=100):
    rng = np.random.default_rng(42)

    return pd.DataFrame(
        {
            "datetime": pd.Timestamp("2026-01-01")
            + pd.to_timedelta(
                np.sort(rng.integers(0, 86400, size=N)),
                unit="s",
            ),
            "object": rng.choice(
                [
                    f"192.168.2.{i}" for i in range(1, 256)
                ],
                size=N,            
            ),
            "event": rng.choice(
                [
                "INVALID_SNI",
                "ASSURED",
                ],
                size=N,
                p=[0.7,0.3],
            ),
        }
    )

events = create_event()

analysis = LifecycleAnalysis(
    df      = events,
    event   = "INVALID_SNI",
    trusted = True,
    ip_col = "object"
)


print(events.head())
print()
print(analysis.summary().head())