import pandas as pd

from lifecycle.analyzer import LifecycleAnalyzer
from lifecycle.analysis_data_builder import AnalysisBuilder
from lifecycle.analysis import LifecycleAnalysis

#
# tests Analyzer API
#


def test_duration_f(sample_analysis_data_f):

    analyzer = LifecycleAnalyzer(sample_analysis_data_f)

    duration = analyzer.duration()

    #
    # NORMAL:
    # False False True True True False False False
    #             ^start      ^end
    # = 3 samples = 3 minutes
    # simple sum of True
    #
    assert duration["NORMAL"] == pd.Timedelta(minutes=3)
    assert duration["SPLIT"] == pd.Timedelta(minutes=4)
    assert duration["PULSE"] == pd.Timedelta(minutes=1)
    assert duration["PULSE2"] == pd.Timedelta(minutes=5)

    assert duration["NEVER"] == pd.Timedelta(minutes=0)

    assert duration["STARTED_BEFORE"] == pd.Timedelta(minutes=3)
    assert duration["ENDED_AFTER"] == pd.Timedelta(minutes=5)
    assert duration["ALWAYS"] == pd.Timedelta(minutes=8)

    assert duration["GAP"] == pd.Timedelta(minutes=7)
    assert duration["EDGE_START"] == pd.Timedelta(minutes=1)
    assert duration["EDGE_END"] == pd.Timedelta(minutes=1)
    assert duration["EDGE_BOTH"] == pd.Timedelta(minutes=2)
    assert duration["ZIGZAG"] == pd.Timedelta(minutes=4)


def test_duration(sample_analysis_data):

    analyzer = LifecycleAnalyzer(sample_analysis_data)

    duration = analyzer.duration()

    #
    # NORMAL:
    # False False True True True False False False
    #             ^start      ^end
    # = 3 samples = 3 minutes
    # simple sum of True
    #
    assert duration["NORMAL"] == pd.Timedelta(minutes=3)
    assert duration["SPLIT"] == pd.Timedelta(minutes=4)
    assert duration["PULSE"] == pd.Timedelta(minutes=1)
    assert duration["PULSE2"] == pd.Timedelta(minutes=5)

    assert duration["NEVER"] == pd.Timedelta(minutes=0)

    assert duration["STARTED_BEFORE"] == pd.Timedelta(minutes=0)
    assert duration["ENDED_AFTER"] == pd.Timedelta(minutes=0)
    assert duration["ALWAYS"] == pd.Timedelta(minutes=0)

    assert duration["GAP"] == pd.Timedelta(minutes=0)
    assert duration["EDGE_START"] == pd.Timedelta(minutes=0)
    assert duration["EDGE_END"] == pd.Timedelta(minutes=0)
    assert duration["EDGE_BOTH"] == pd.Timedelta(minutes=0)
    assert duration["ZIGZAG"] == pd.Timedelta(minutes=3)


def test_segment_duration(sample_analysis_data):

    analyzer = LifecycleAnalyzer(sample_analysis_data)

    duration = analyzer.segment_duration()

    assert duration["NORMAL", 1] == pd.Timedelta(minutes=3)

    assert duration["SPLIT", 1] == pd.Timedelta(minutes=2)
    assert duration["SPLIT", 2] == pd.Timedelta(minutes=2)

    assert duration["PULSE", 1] == pd.Timedelta(minutes=1)

    assert duration["PULSE2", 1] == pd.Timedelta(minutes=3)
    assert duration["PULSE2", 2] == pd.Timedelta(minutes=2)

    assert duration["ZIGZAG", 1] == pd.Timedelta(minutes=1)
    assert duration["ZIGZAG", 2] == pd.Timedelta(minutes=1)
    assert duration["ZIGZAG", 3] == pd.Timedelta(minutes=1)

    assert "NEVER" not in duration.index.get_level_values(0)

def test_mean_segment_duration(sample_analysis_data):

    analyzer = LifecycleAnalyzer(sample_analysis_data)

    mean = analyzer.mean_segment_duration()

    assert mean["NORMAL"] == pd.Timedelta(minutes=3)

    assert mean["SPLIT"] == pd.Timedelta(minutes=2)

    assert mean["PULSE"] == pd.Timedelta(minutes=1)

    assert mean["PULSE2"] == pd.Timedelta(minutes=2.5)

    assert mean["ZIGZAG"] == pd.Timedelta(minutes=1)

def test_max_segment_duration(sample_analysis_data):

    analyzer = LifecycleAnalyzer(sample_analysis_data)

    maximum = analyzer.max_segment_duration()

    assert maximum["NORMAL"] == pd.Timedelta(minutes=3)

    assert maximum["SPLIT"] == pd.Timedelta(minutes=2)

    assert maximum["PULSE2"] == pd.Timedelta(minutes=3)

    assert maximum["ZIGZAG"] == pd.Timedelta(minutes=1)

def test_min_segment_duration(sample_analysis_data):

    analyzer = LifecycleAnalyzer(sample_analysis_data)

    minimum = analyzer.min_segment_duration()

    assert minimum["NORMAL"] == pd.Timedelta(minutes=3)

    assert minimum["SPLIT"] == pd.Timedelta(minutes=2)

    assert minimum["PULSE2"] == pd.Timedelta(minutes=2)

    assert minimum["ZIGZAG"] == pd.Timedelta(minutes=1)


def test_mean_segment_duration_seconds(sample_analysis_data):

    analyzer = LifecycleAnalyzer(sample_analysis_data)

    mean = analyzer.mean_segment_duration_seconds()

    assert mean["NORMAL"] == 180

    assert mean["SPLIT"] == 120

    assert mean["PULSE"] == 60

    assert mean["PULSE2"] == 150

    assert mean["ZIGZAG"] == 60

def test_max_segment_duration_seconds(sample_analysis_data):

    analyzer = LifecycleAnalyzer(sample_analysis_data)

    maximum = analyzer.max_segment_duration_seconds()

    assert maximum["NORMAL"] == 180

    assert maximum["SPLIT"] == 120

    assert maximum["PULSE2"] == 180

    assert maximum["ZIGZAG"] == 60

def test_min_segment_duration(sample_analysis_data):

    analyzer = LifecycleAnalyzer(sample_analysis_data)

    minimum = analyzer.min_segment_duration_seconds()

    assert minimum["NORMAL"] == 180

    assert minimum["SPLIT"] == 120

    assert minimum["PULSE2"] == 120

    assert minimum["ZIGZAG"] == 60

def test_segment_duration_f(sample_analysis_data_f):

    analyzer = LifecycleAnalyzer(sample_analysis_data_f)

    duration = analyzer.segment_duration()

    assert duration["STARTED_BEFORE", 1] == pd.Timedelta(minutes=3)

    assert duration["ENDED_AFTER", 1] == pd.Timedelta(minutes=5)

    assert duration["ALWAYS", 1] == pd.Timedelta(minutes=8)

    assert duration["GAP", 1] == pd.Timedelta(minutes=4)
    assert duration["GAP", 2] == pd.Timedelta(minutes=3)

def test_segment_count(sample_analysis_data):

    analyzer = LifecycleAnalyzer(sample_analysis_data)

    count = analyzer.segment_count()


    assert count["NORMAL"] == 1
    assert count["SPLIT"] == 2
    assert count["PULSE"] == 1
    assert count["PULSE2"] == 2

    assert count["NEVER"] == 0

    assert count["STARTED_BEFORE"] == 0
    assert count["ENDED_AFTER"] == 0
    assert count["ALWAYS"] == 0

    assert count["GAP"] == 0
    assert count["EDGE_START"] == 0
    assert count["EDGE_END"] == 0
    assert count["EDGE_BOTH"] == 0

    assert count["ZIGZAG"] == 3


def test_summary(sample_analysis_data):

    analyzer = LifecycleAnalyzer(sample_analysis_data)

    summary = analyzer.summary()

    print(summary.T)

    #
    # Time
    #
    assert summary.loc["NORMAL", "duration"] == pd.Timedelta(minutes=3)
    assert summary.loc["NORMAL", "active_duration"] == 3

    #
    # Structure
    #
    assert summary.loc["NORMAL", "samples"] == 3
    assert summary.loc["NORMAL", "segments"] == 1

    assert summary.loc["SPLIT", "samples"] == 4
    assert summary.loc["SPLIT", "segments"] == 2

    #
    # Observation
    #
    assert summary.loc["NORMAL", "started_before"] == False
    assert summary.loc["NORMAL", "ended_after"] == False
    assert summary.loc["NORMAL", "complete"] == True
    assert summary.loc["NORMAL", "coverage_ratio"] == 1.0

    #
    # Quality
    #
    assert summary.loc["NORMAL", "duplicate"] == False
    assert summary.loc["NORMAL", "orphan"] == False
    assert summary.loc["NORMAL", "good"] == True

    assert summary.loc["NORMAL", "active_duration"] == 3
    assert summary.loc["NORMAL", "duplicate"] == False
    assert summary.loc["NORMAL", "orphan"] == False
    assert summary.loc["NORMAL", "good"] == True

    assert summary.loc["SPLIT", "segments"] == 2

    assert summary.loc["STARTED_BEFORE", "started_before"]
    assert not summary.loc["NORMAL", "started_before"]

    assert summary.loc["NORMAL", "good"]
    assert not summary.loc["NORMAL", "duplicate"]

def test_summary_segment_features(sample_analysis_data):

    analyzer = LifecycleAnalyzer(sample_analysis_data)

    summary = analyzer.summary()

    #
    # Segment
    #
    assert summary.loc["NORMAL", "segment_count"] == 1
    assert summary.loc["SPLIT", "segment_count"] == 2
    assert summary.loc["PULSE", "segment_count"] == 1
    assert summary.loc["PULSE2", "segment_count"] == 2
    assert summary.loc["NEVER", "segment_count"] == 0
    assert summary.loc["ZIGZAG", "segment_count"] == 3


    #
    # Mean
    #
    assert summary.loc[
        "NORMAL",
        "mean_segment_duration"
    ] == pd.Timedelta(minutes=3)

    assert summary.loc[
        "SPLIT",
        "mean_segment_duration"
    ] == pd.Timedelta(minutes=2)

    assert summary.loc[
        "PULSE2",
        "mean_segment_duration"
    ] == pd.Timedelta(minutes=2.5)


    #
    # Max
    #
    assert summary.loc[
        "PULSE2",
        "max_segment_duration"
    ] == pd.Timedelta(minutes=3)


    #
    # Min
    #
    assert summary.loc[
        "PULSE2",
        "min_segment_duration"
    ] == pd.Timedelta(minutes=2)

    assert summary.loc[
        "ZIGZAG",
        "min_segment_duration"
    ] == pd.Timedelta(minutes=1)


def test_statistics(sample_analysis_data):

    analyzer = LifecycleAnalyzer(sample_analysis_data)

    stats = analyzer.statistics()

    #print(stats)

    #
    # 必要な列があること
    #
    assert "duration" in stats.columns
    assert "samples" in stats.columns
    assert "segments" in stats.columns
 #   assert "transitions" in stats.columns


    #
    # 件数
    #
    assert stats.loc["count", "samples"] == 13


    #
    # 最大値
    #
    assert stats.loc["max", "segments"] == 3

    #
    # duration最大
    #
    assert (
        stats.loc["max", "duration"]
        ==
        5 * 60
    )

def test_lifetime_distribution(sample_analysis_data):

    analyzer = LifecycleAnalyzer(sample_analysis_data)

    dist = analyzer.lifetime_distribution()

    assert dist["NORMAL"] == pd.Timedelta(minutes=3)

    assert dist["SPLIT"] == pd.Timedelta(minutes=4)

    assert dist["PULSE"] == pd.Timedelta(minutes=1)

    assert dist["PULSE2"] == pd.Timedelta(minutes=5)

    assert dist["NEVER"] == pd.Timedelta(minutes=0)

    assert dist["ZIGZAG"] == pd.Timedelta(minutes=3)

def test_segment_distribution(sample_analysis_data):

    analyzer = LifecycleAnalyzer(sample_analysis_data)

    dist = analyzer.segment_distribution()

    assert dist["NORMAL", 1] == pd.Timedelta(minutes=3)

    assert dist["SPLIT", 1] == pd.Timedelta(minutes=2)
    assert dist["SPLIT", 2] == pd.Timedelta(minutes=2)

    assert dist["PULSE", 1] == pd.Timedelta(minutes=1)

    assert dist["PULSE2", 1] == pd.Timedelta(minutes=3)
    assert dist["PULSE2", 2] == pd.Timedelta(minutes=2)

    assert dist["ZIGZAG", 1] == pd.Timedelta(minutes=1)
    assert dist["ZIGZAG", 2] == pd.Timedelta(minutes=1)
    assert dist["ZIGZAG", 3] == pd.Timedelta(minutes=1)

def test_segment_distribution_f(sample_analysis_data_f):

    analyzer = LifecycleAnalyzer(sample_analysis_data_f)

    dist = analyzer.segment_distribution()

    assert dist["STARTED_BEFORE", 1] == pd.Timedelta(minutes=3)

    assert dist["ENDED_AFTER", 1] == pd.Timedelta(minutes=5)

    assert dist["ALWAYS", 1] == pd.Timedelta(minutes=8)

    assert dist["GAP", 1] == pd.Timedelta(minutes=4)
    assert dist["GAP", 2] == pd.Timedelta(minutes=3)



def test_histogram_duration(sample_analysis_data):

    analyzer = LifecycleAnalyzer(sample_analysis_data)
 

    hist = analyzer.histogram(
        "duration",
        bins=4,
    )

    print(hist)

    assert "count" in hist.columns
    assert "left" in hist.columns
    assert "right" in hist.columns


    #
    # 全Lifecycle数
    #
    assert hist["count"].sum() == 13


def test_lifecycle_analysis(sample_events):

    analysis = LifecycleAnalysis(
        sample_events,
        event="ASSURED",
    )

    summary = analysis.summary()

    assert isinstance(
        summary,
        pd.DataFrame,
    )

    assert "duration" in summary.columns
    assert "segment_count" in summary.columns

    assert len(summary) > 0
    
def test_lifecycle_analysis_trusted(sample_events):

    analysis_t = LifecycleAnalysis(
        sample_events,
        event="ASSURED",
        trusted=True,
    )

    analysis_f = LifecycleAnalysis(
        sample_events,
        event="ASSURED",
        trusted=False,
    )

    assert isinstance(
        analysis_t.summary(),
        pd.DataFrame,
    )

    assert isinstance(
        analysis_f.summary(),
        pd.DataFrame,
    )



