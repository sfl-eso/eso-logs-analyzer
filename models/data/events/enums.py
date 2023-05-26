from enum import Enum


class EffectType(Enum):
    BUFF = "BUFF"
    DEBUFF = "DEBUFF"


class StatusEffectType(Enum):
    pass


class Server(Enum):
    EU = "EU Megaserver"
    NA = "NA Megaserver"


class Locale(Enum):
    EN = "en"


class TrialId(Enum):
    CLOUDREST = "9"
    ROCKGROVE = "15"


class ZoneDifficulty(Enum):
    NONE = "NONE"
    NORMAL = "NORMAL"
    VETERAN = "VETERAN"


class Hostility(Enum):
    HOSTILE = "HOSTILE"
    NPC_ALLY = "NPC_ALLY"
    PLAYER_ALLY = "PLAYER_ALLY"


class ClassId(Enum):
    pass


class RaceId(Enum):
    pass


class UnitType(Enum):
    MONSTER = "MONSTER"
    OBJECT = "OBJECT"
    PLAYER = "PLAYER"


class CastStatus(Enum):
    COMPLETED = "COMPLETED"
    PLAYER_CANCELLED = "PLAYER_CANCELLED"
    INTERRUPTED = "INTERRUPTED"


class EffectChangedStatus(Enum):
    GAINED = "GAINED"
    UPDATED = "UPDATED"
    FADED = "FADED"


class CombatEventType(Enum):
    HOT_TICK = "HOT_TICK"
    HOT_TICK_CRITICAL = "HOT_TICK_CRITICAL"
    QUEUED = "QUEUED"
    ABILITY_ON_COOLDOWN = "ABILITY_ON_COOLDOWN"


class DamageType(Enum):
    GENERIC = "GENERIC"
    INVALID = "INVALID"


class ResourceType(Enum):
    MAGICKA = "MAGICKA"
    INVALID = "INVALID"
