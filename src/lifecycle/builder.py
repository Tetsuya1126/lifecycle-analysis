from __future__ import annotations

import pandas as pd

from .model import (
    Lifecycle,
)

from .pipelines.presence import (
    _presence_from_events,
    _presence_resample,
    _transition_from_presence,
    _observation_from_presence,
    _state_from_transition,
    _sample_interval,
)


class LifecycleBuilder:

    @classmethod
    def from_events(
        cls,
        df: pd.DataFrame,
        *,
        event: str,
        name: str | None = None,
        event_col: str = "event",
        time_col: str = "datetime",
        ip_col: str = "ip",
        interval: str | None = None,
    ) -> Lifecycle:
        """
        Raw Event DataFrameからLifecycleを生成する。
        """

        if name is None:
            name = event

        presence = _presence_from_events(
            df,
            event=event,
            event_col=event_col,
            time_col=time_col,
            ip_col=ip_col,
        )
        
        if presence.empty:
            raise ValueError(
            "empty presence dataframe"
        )


        if interval is not None:
            presence = _presence_resample(
                presence,
                interval=interval,
            )
        
        return cls.from_presence(
            presence,
            name=name,
        )


    @classmethod
    def from_presence(
        cls,
        presence: pd.DataFrame,
        *,
        name: str,
    ) -> Lifecycle:
        """
        Presence(bool)からLifecycleを生成する。
        """
        #
        # Derived from Presence
        #
        sample_interval = _sample_interval(
            presence.index,
        )
        #
        # State Pipeline
        #
        transition = _transition_from_presence(
            presence,
        )

        state = _state_from_transition(
            transition,
        )
        #
        # Observation
        #
        observation = _observation_from_presence(
            presence,
        )

        return Lifecycle(
            name=name,

            presence=presence,
            transition=transition,
            state=state,
            
            observation=observation,
            
            sample_interval=sample_interval,
        )
 
