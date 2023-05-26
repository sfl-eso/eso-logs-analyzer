from datetime import timedelta

from .enums import TrialId
from .event import Event


class TrialInit(Event):
    """
    Event happens when player teleports into a trial. That trial may be in process or already finished
    """

    event_type: str = "TRIAL_INIT"

    def __init__(self, id: int, trial_id: str, in_progress: str, completed: str, start_time_in_ms: str, duration_in_ms,
                 success: str, final_score: str):
        super(TrialInit, self).__init__(id)
        self.trial_id: TrialId = TrialId(trial_id)
        # True if the trial is already in progress
        self.in_progress = in_progress == "T"
        # True if the trial was already completed
        self.completed = completed == "T"
        # Time when the trial was started
        self.start_time = timedelta(milliseconds=int(start_time_in_ms))
        # Duration of the trial
        self.duration = timedelta(milliseconds=int(duration_in_ms))
        # True, if the trial was successfully finished (can this ever be false when trial is complete?)
        self.success = success == "T"
        # Final score of the trial
        self.final_score = int(final_score)
