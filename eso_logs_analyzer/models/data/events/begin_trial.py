from __future__ import annotations

from typing import TYPE_CHECKING

from .enums import TrialId
from .event import Event
from .span_event import SpanCast
from ....utils import parse_epoch_time

if TYPE_CHECKING:
    from .end_trial import EndTrial


class BeginTrial(SpanCast):
    """
    Technically the epoch time is "startTimeMS"
    """

    event_type: str = "BEGIN_TRIAL"

    def __init__(self, event_id: int, trial_id: str, epoch_time: str):
        super(BeginTrial, self).__init__(event_id)
        # The timestamp when the trial started
        self.time = parse_epoch_time(epoch_time)
        # Id of the trial
        self.trial_id: TrialId = TrialId(trial_id)

        # The corresponding end event
        self.end_trial: EndTrial = None

    # def event_time(self, event_id: int) -> datetime:
    #     return self.time + timedelta(milliseconds=(event_id - self.id))

    @property
    def end_event(self) -> Event:
        return self.end_trial

    @end_event.setter
    def end_event(self, value: Event):
        self.end_trial = value
