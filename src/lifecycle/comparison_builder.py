from .model import AnalysisData
from .comparison import LifecycleComparison

class ComparisonBuilder:

    @classmethod
    def from_analysis(
        cls,
        left: AnalysisData,
        right: AnalysisData,
    ) -> LifecycleComparison:
        
        activity_left = left.activity
        activity_right = right.activity

        A = activity_left.lifetime
        B = activity_right.lifetime    
  
        return LifecycleComparison(
            left_name=left.name,
            right_name=right.name,

            overlap=A & B,
            only_left=A & ~B,
            only_right=~A & B,
            union=A | B,
        )