import pandas as pd
import numpy as np

from lifecycle import (
    LifecycleAnalysis,
)

N = 100
rng = np.random.default_rng(42)

events = pd.DataFrame(
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
                "login",
                "logout",
            ],
            size=N,
            p=[0.5,0.5],
        ),
    }
)


analysis = LifecycleAnalysis(
    df      = events,
    event   = "login",
    trusted = True,
    ip_col = "object"
)


print(events.head())
print()
print(analysis.summary().head())