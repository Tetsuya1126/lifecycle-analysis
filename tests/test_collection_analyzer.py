from pandas.testing import assert_frame_equal

from lifecycle.collection import LifecycleCollection
from lifecycle.collection_analyzer import CollectionAnalyzer
from .conftest import make_analysis

def test_overlap_matrix(sample_analysis_data):

    collection = LifecycleCollection(
        analyses={
            "A": sample_analysis_data,
            "B": sample_analysis_data,
        }
    )

    analyzer = CollectionAnalyzer(collection)

    result = analyzer.overlap_count_matrix()

    assert result.loc["A", "A"] > 0
    assert result.loc["B", "B"] > 0
    assert result.loc["A", "B"] == result.loc["B", "A"]


def test_containment_matrix(sample_analysis_data):

    collection = LifecycleCollection(
        analyses={
            "A": sample_analysis_data,
            "B": sample_analysis_data,
        }
    )

    analyzer = CollectionAnalyzer(collection)

    result = analyzer.containment_matrix()

    assert result.loc["A", "A"] == 1.0
    assert result.loc["A", "B"] == 1.0
    assert result.loc["B", "A"] == 1.0
    assert result.loc["B", "B"] == 1.0


def test_containment_matrix_partial(sample_presence):

    normal = make_analysis(
        sample_presence,
        name="NORMAL",
        columns=["NORMAL"],
    )

    pulse = make_analysis(
        sample_presence,
        name="PULSE",
        columns=["PULSE"],
    )

    collection = LifecycleCollection(
        analyses={
            "NORMAL": normal,
            "PULSE": pulse,
        }
    )

    analyzer = CollectionAnalyzer(collection)

    result = analyzer.containment_matrix()


    assert result.loc["NORMAL", "NORMAL"] == 1.0
    assert result.loc["PULSE", "PULSE"] == 1.0

    assert result.loc["PULSE", "NORMAL"] == 1.0
    assert result.loc["NORMAL", "PULSE"] == 1/3


def test_transition_matrix(sample_analysis_data):

    collection = LifecycleCollection(
        analyses={
            "A": sample_analysis_data,
            "B": sample_analysis_data,
        }
    )

    analyzer = CollectionAnalyzer(collection)

    result = analyzer.transition_matrix()

    assert result.loc["A", "A"] == 1.0
    assert result.loc["A", "B"] == 1.0