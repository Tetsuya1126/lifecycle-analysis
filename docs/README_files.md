```
lifecycle-analysis$ tree -L 5
.
├── LICENSE
├── README.md
├── README_jp.md
├── benchmarks
│   ├── 20260712-20:17_profile.out
│   └── 20260713-07:30_profile.out
├── docs
│   ├── README_detail.md
│   ├── README_files.md
│   ├── README_models.md
│   └── memo.md
├── examples
│   ├── bench_mark.py
│   └── quick_start.py
├── pyproject.toml
├── src
│   ├── lifecycle
│   │   ├── __init__.py
│   │   ├── analysis.py
│   │   ├── analysis_data_builder.py
│   │   ├── analyzer.py
│   │   ├── builder.py
│   │   ├── collection.py
│   │   ├── collection_analyzer.py
│   │   ├── comparison.py
│   │   ├── comparison_analyzer.py
│   │   ├── comparison_builder.py
│   │   ├── model.py
│   │   ├── pipelines
│   │   │   ├── __init__.py
│   │   │   ├── activity.py
│   │   │   ├── pandas_converter.py
│   │   │   ├── presence.py
│   │   │   └── quality.py
│   │   └── pipelines_pandas_version
│   │       ├── activity.py
│   │       ├── presence.py
│   │       └── quality.py
│   └── lifecycle_analysis.egg-info
│       ├── PKG-INFO
│       ├── SOURCES.txt
│       ├── dependency_links.txt
│       ├── requires.txt
│       └── top_level.txt
└── tests
    ├── __init__.py
    ├── asserts.py
    ├── conftest.py
    ├── test_analysis_builder.py
    ├── test_analyzer.py
    ├── test_builder.py
    ├── test_collection_analyzer.py
    ├── test_comparison_builder.py
    ├── test_pipeline_activity.py
    ├── test_pipeline_presence.py
    └── test_pipeline_quality.py

13 directories, 74 files

```