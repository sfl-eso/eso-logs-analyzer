from enum import Enum
from typing import List

from models.data.events import UnitAdded
from models.data.events.enums import TrialId


class Rockgrove(Enum):
    OAXILTSO = "Oaxiltso"
    BAHSEI = "Flame-Herald Bahsei"
    # XALVAKKA = "Xalvakka"


def get_boss_for_trial(trialId: TrialId, boss_units: List[UnitAdded]):
    if len(boss_units) == 1:
        if trialId == TrialId.ROCKGROVE:
            return Rockgrove(boss_units[0].name)
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError
