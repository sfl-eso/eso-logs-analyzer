from __future__ import annotations

from enum import Enum
from typing import List, TYPE_CHECKING

from ..models.data.events.enums import TrialId

if TYPE_CHECKING:
    from ..models.postprocessing import Unit


class Rockgrove(Enum):
    OAXILTSO = "Oaxiltso"
    BAHSEI = "Flame-Herald Bahsei"
    # XALVAKKA = "Xalvakka"


def get_boss_for_trial(trialId: TrialId, boss_units: List[Unit]):
    if len(boss_units) == 1:
        if trialId == TrialId.ROCKGROVE:
            return Rockgrove(boss_units[0].unit.name)
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError
