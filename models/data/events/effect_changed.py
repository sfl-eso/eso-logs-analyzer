from .enums import EffectChangedStatus
from .target_event import TargetEvent


class EffectChanged(TargetEvent):
    event_type: str = "EFFECT_CHANGED"

    def __init__(self,
                 id: int,
                 status: str,
                 stack_count: str,
                 cast_effect_id: str,
                 ability_id: str,
                 unit_id: str,
                 health: str,
                 magicka: str,
                 stamina: str,
                 ultimate: str,
                 werewolf_ultimate: str,
                 shield: str,
                 x_coord: str,
                 y_coord: str,
                 heading_radians: str,
                 target_unit_id: str,
                 target_health: str = None,
                 target_magicka: str = None,
                 target_stamina: str = None,
                 target_ultimate: str = None,
                 target_werewolf_ultimate: str = None,
                 target_shield: str = None,
                 target_x_coord: str = None,
                 target_y_coord: str = None,
                 target_heading_radians: str = None,
                 player_initiated_remove_cast_track_id: str = None):
        super(EffectChanged, self).__init__(id=id,
                                            ability_id=ability_id,
                                            unit_id=unit_id,
                                            health=health,
                                            magicka=magicka,
                                            stamina=stamina,
                                            ultimate=ultimate,
                                            werewolf_ultimate=werewolf_ultimate,
                                            shield=shield,
                                            x_coord=x_coord,
                                            y_coord=y_coord,
                                            heading_radians=heading_radians,
                                            target_unit_id=target_unit_id,
                                            target_health=target_health,
                                            target_magicka=target_magicka,
                                            target_stamina=target_stamina,
                                            target_ultimate=target_ultimate,
                                            target_werewolf_ultimate=target_werewolf_ultimate,
                                            target_shield=target_shield,
                                            target_x_coord=target_x_coord,
                                            target_y_coord=target_y_coord,
                                            target_heading_radians=target_heading_radians)
        self.status: EffectChangedStatus = EffectChangedStatus[status]
        self.stack_count = int(stack_count)
        self.cast_effect_id = int(cast_effect_id)
        self.player_initiated_remove_cast_track_id = player_initiated_remove_cast_track_id

        self.gained_event: TargetEvent = None
        self.faded_event: TargetEvent = None
