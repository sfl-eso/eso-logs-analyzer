from .enums import EffectType, StatusEffectType
from .event import Event


class EffectInfo(Event):
    event_type: str = "EFFECT_INFO"

    def __init__(self,
                 id: int,
                 ability_id: str,
                 effect_type: str,
                 status_effect_type: str,
                 no_effect_bar: str,
                 grants_synergy_ability_id: str = None):
        super(EffectInfo, self).__init__(id)
        # Id of the ability (same as ingame)
        self.ability_id = int(ability_id)
        # What kind of effect this is (i.e., buff, debuff)
        self.effect_type: EffectType = EffectType(effect_type)
        # TODO: which values can this be
        self.status_effect_type: StatusEffectType = StatusEffectType(status_effect_type)
        # TODO: which values can this be
        # TODO: is this still true with "T" "F" values?
        # TODO: separate function to convert these values that throws an exception if the values changed (i.e., not T and not F)
        self.no_effect_bar = no_effect_bar == "T"
        # If set, this ability id is the synergy granted by this effect
        # TODO: integrate into ability_info or get ability info object
        self.grants_synergy_ability_id = grants_synergy_ability_id
