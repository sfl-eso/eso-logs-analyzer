from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from .enums import TrialId
from .event import Event

if TYPE_CHECKING:
    from .begin_trial import BeginTrial


class EndTrial(Event):
    event_type: str = "END_TRIAL"

    def __init__(self, id: int, trial_id: str, trial_duration_ms: str, success: str, final_score: str,
                 final_vitality_bonus: str):
        super(EndTrial, self).__init__(id)
        # Id of the trial
        self.trial_id: TrialId = TrialId(trial_id)
        # Time of the completion (i.e., how long it took)
        self.trial_duration = timedelta(milliseconds=int(trial_duration_ms))
        # If the trial was cleared successfully (can this ever be false?)
        self.success = success == "T"
        # Final score
        self.final_score = int(final_score)
        # Vitality bonus to the score
        self.final_vitality_bonus = int(final_vitality_bonus)

        # The corresponding begin trial event
        self.begin_trial: BeginTrial = None
