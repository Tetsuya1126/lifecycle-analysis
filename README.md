# Lifecycle Analysis

[![Tests](https://github.com/Tetsuya1126/lifecycle-analysis/actions/workflows/test.yaml/badge.svg)](https://github.com/Tetsuya1126/lifecycle-analysis/actions/workflows/test.yaml)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/github/license/Tetsuya1126/lifecycle-analysis)

> **Lifecycle Analysis achieves reliable and reproducible lifecycle analysis by explicitly separating *observed data* from *analyzable data*.**

Lifecycle Analysis is a Python library for extracting lifecycles (periods of existence) from time-series event data and performing statistical analysis.

Originally developed for firewall connection event analysis, the library has since been generalized to support a wide range of time-series datasets.

Trust your lifecycle statistics by analyzing only complete and reliable lifecycles.

---

# Why Lifecycle Analysis?

In lifecycle analysis, **not every observed lifecycle should be used for statistical analysis.**

For example:

* Objects that already existed before the observation period
* Objects that continue to exist after the observation period
* Lifecycles containing inconsistent or invalid state transitions

Although these lifecycles are observable, they do not necessarily represent complete lifecycle information.

---

# Features

Lifecycle Analysis is built around the following principle:

> **Observed data and analyzable data are not the same.**

Its architecture therefore separates observation from analysis:

```text
  Observed Events
        │
        ▼
    Lifecycle
 (Observed Facts)
        │
        ▼
   AnalysisData
 (Trusted Data)
        │
        ▼
 LifecycleAnalyzer
```

Only trusted lifecycles are included in statistical analysis.

---

# Typical Use Cases

Lifecycle Analysis can be applied to many types of event-based datasets, including:

* Firewall / VPN connection logs
* User login/logout histories
* IoT sensor events
* System uptime monitoring
* Manufacturing equipment logs
* Service usage histories
* Any other time-series event data

---

# Installation

Clone the repository and install the package:

```bash
git clone https://github.com/Tetsuya1126/lifecycle-analysis.git

cd lifecycle-analysis

pip install -e .
```

---

# Quick Start

The following example generates lifecycles from login events and computes summary statistics.

`LifecycleAnalysis` is a high-level API that internally combines `LifecycleBuilder`, `AnalysisBuilder`, and `LifecycleAnalyzer`.

```python
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
                p=[0.7, 0.3],
            ),
        }
    )


events = create_event()

analysis = LifecycleAnalysis(
    df=events,
    event="INVALID_SNI",
    trusted=True,
    ip_col="object",
)

print(events.head())
print()
print(analysis.summary().head())
```

---

# Input Data

The input is expected to be a `pandas.DataFrame` containing time-series events.

At minimum, the dataset should include:

| Column   | Description                            |
| -------- | -------------------------------------- |
| datetime | Event timestamp (`datetime`)           |
| ip       | Target object (IP, user, device, etc.) |
| event    | Event type                             |

Example:

```text
             datetime      ip        event
0 2026-01-01 10:00     host01      login
1 2026-01-01 10:10     host01      logout
2 2026-01-01 10:30     host02      login
```

The column names are not fixed.

`LifecycleBuilder` can be configured to work with various event formats by specifying the required columns.

---

# Architecture

The library follows a single-responsibility design.

| Component         | Responsibility                        |
| ----------------- | ------------------------------------- |
| LifecycleBuilder  | Builds a `Lifecycle` from raw events  |
| Lifecycle         | Stores observed lifecycle information |
| AnalysisBuilder   | Produces analysis-ready data          |
| AnalysisData      | Stores trusted analysis data          |
| LifecycleAnalyzer | Performs statistical analysis         |

Each component has a clearly defined responsibility.

---

A lifecycle is constructed step by step using **Presence** as the foundation.

```text
                Raw Events
                   │
                   ▼
          +----------------------+
          | LifecycleBuilder     |
          +----------------------+
                   │
                   ▼
          +----------------------+
          | Lifecycle            |
          | • Presence           |
          | • Transition         |
          | • State              |
          | • Observation        |
          | • Sample Interval    |
          +----------------------+
                   │
                   ▼
          +----------------------+
          | AnalysisBuilder      |
          +----------------------+
                   │
                   ▼
          +----------------------+
          | AnalysisData         |
          | • Name               |
          | • Raw State          |
          | • Sample Interval    |
          | • Quality            |
          | • Analysis Filter    |
          | • Activity           |
          |   - Lifetime         |
          |   - Boundary         |
          |   - Segment Length   |
          +----------------------+
                   │
                   ▼
          +----------------------+
          | LifecycleAnalyzer    |
          +----------------------+
                   │
                   ▼
            Summary / Statistics
```

Most operations are implemented using vectorized NumPy and pandas computations.

---

# Trusted Analysis

Before performing statistical analysis, two independent quality checks are applied:

* **Observation Quality**
* **State Transition Quality**

```text
Observation
(Observed Data)

↓

Trusted Mask
(Remove Observation Boundaries)

↓

Quality Mask
(Remove Invalid States)

↓

Analysis Mask
```

```python
analysis_mask = (
    observation.trusted_mask
    &
    quality.good
)
```

This excludes:

* Lifecycles that started before the observation period
* Lifecycles that continue after the observation period
* Lifecycles containing invalid state transitions

As a result, only trusted lifecycles contribute to statistical analysis.

---

# Performance

Lifecycle Analysis is designed for large-scale time-series datasets.

Key design principles:

* Vectorized NumPy / pandas operations
* Minimal Python loops
* Immutable data models
* Reduced memory usage with `slots=True`
* Reproducible analysis

---

# Documentation

Detailed design documents are available in the `docs/` directory.

```text
docs/
├── README_calc_bit_vector.md
├── README_detail.md
├── README_files.md
└── README_models.md

```

These documents describe:

* Design philosophy
* Data flow
* Lifecycle model
* AnalysisData model
* Bit-matrix operations
* Observation masks
* Quality masks
* Boundary analysis

---

# Roadmap

* [x] Lifecycle Builder
* [x] Analysis Builder
* [x] Lifecycle Analyzer (core features)
* [x] Lifecycle Comparison (core features)
* [ ] Additional statistical methods
* [ ] Collection Analysis
* [ ] Survival Analysis
* [ ] Visualization
* [ ] Polars Backend

---

# License

Released under the MIT License.

