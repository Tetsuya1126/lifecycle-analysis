import pandas as pd

from .model import (
    Lifecycle,
    AnalysisData,
)

from .pipelines.quality import (
    _quality_from_state,
)

from .pipelines.activity import (
    _activity_from_state,
)


class AnalysisBuilder:

    @classmethod
    def from_lifecycle(
        cls,
        lifecycle: Lifecycle,
        *,
        trusted: bool = True,
    ) -> AnalysisData:

        #
        # Raw State
        #
        raw_state = lifecycle.state

        sample_interval = lifecycle.sample_interval

        #
        # Quality (Raw State)
        #
        quality = _quality_from_state(
            raw_state,
        )

        #
        # Analysis Mask
        #
        if trusted:

            analysis_mask = (
                lifecycle.observation.trusted_mask
                &
                quality.good
            )

        else:

            analysis_mask = pd.DataFrame(
                True,
                index=raw_state.index,
                columns=raw_state.columns,
            )

        #
        # Analysis State
        #
        analysis_state = raw_state.where(
            analysis_mask,
            0,
        )

        #
        # Activity Analysis
        #
        activity = _activity_from_state(
            analysis_state,
        )

        return AnalysisData(
            name=lifecycle.name,

            
            raw_state=raw_state,

            sample_interval=sample_interval,

            quality=quality,

            analysis_mask=analysis_mask,
            analysis_state=analysis_state,

            activity=activity,
        )




