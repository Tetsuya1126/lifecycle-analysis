from dataclasses import dataclass

from .model import AnalysisData
from .comparison import LifecycleComparison
from .comparison_builder import ComparisonBuilder


@dataclass(slots=True, frozen=True)
class LifecycleCollection:
    """
    AnalysisData の集合
    """

    analyses: dict[str, AnalysisData]

    def names(self) -> list[str]:
        return list(self.analyses.keys())

    def get(self, name: str) -> AnalysisData:
        return self.analyses[name]

    def compare(
        self,
        left: str,
        right: str,
    ) -> LifecycleComparison:

        return ComparisonBuilder.from_analysis(
            self.analyses[left],
            self.analyses[right],
        )