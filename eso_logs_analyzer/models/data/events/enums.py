from enum import Enum


class EffectType(Enum):
    BUFF = "BUFF"
    DEBUFF = "DEBUFF"


class StatusEffectType(Enum):
    NONE = "NONE"
    BLEED = "BLEED"
    MAGIC = "MAGIC"
    POISON = "POISON"
    ROOT = "ROOT"
    SNARE = "SNARE"


class NoEffectBar(Enum):
    NEVER = "NEVER"
    DEFAULT = "DEFAULT"


class Server(Enum):
    EU = "EU Megaserver"
    NA = "NA Megaserver"


class Locale(Enum):
    EN = "en"


class TrialId(Enum):
    ASYLUM_SANCTORIUM = "8"
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
    FRIENDLY = "FRIENDLY"
    NEUTRAL = "NEUTRAL"


class ClassId(Enum):
    INVALID = "0"
    DRAGONKNIGHT = "1"
    SORCERER = "2"
    NIGHTBLADE = "3"
    WARDEN = "4"
    NECROMANCER = "5"
    TEMPLAR = "6"
    ARCANIST = "117"


class RaceId(Enum):
    INVALID = "0"
    BRETON = "1"
    # INVALID2 = "2"
    # INVALID3 = "3"
    DUNMER = "4"
    NORD = "5"
    # INVALID6 = "6"
    ALTMER = "7"
    # INVALID8 = "8"
    KHAJIIT = "9"
    IMPERIAL = "10"


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
    ABILITY_ON_COOLDOWN = "ABILITY_ON_COOLDOWN"
    BAD_TARGET = "BAD_TARGET"
    BLOCKED_DAMAGE = "BLOCKED_DAMAGE"
    BUSY = "BUSY"
    CANNOT_USE = "CANNOT_USE"
    CANT_SEE_TARGET = "CANT_SEE_TARGET"
    CASTER_DEAD = "CASTER_DEAD"
    CRITICAL_DAMAGE = "CRITICAL_DAMAGE"
    CRITICAL_HEAL = "CRITICAL_HEAL"
    DAMAGE = "DAMAGE"
    DAMAGE_SHIELDED = "DAMAGE_SHIELDED"
    DIED = "DIED"
    DIED_XP = "DIED_XP"
    DISORIENTED = "DISORIENTED"
    DODGED = "DODGED"
    DOT_TICK_CRITICAL = "DOT_TICK_CRITICAL"
    DOT_TICK = "DOT_TICK"
    FAILED = "FAILED"
    FAILED_REQUIREMENTS = "FAILED_REQUIREMENTS"
    FEARED = "FEARED"
    HEAL = "HEAL"
    HOT_TICK = "HOT_TICK"
    HOT_TICK_CRITICAL = "HOT_TICK_CRITICAL"
    IMMUNE = "IMMUNE"
    INSUFFICIENT_RESOURCE = "INSUFFICIENT_RESOURCE"
    INTERRUPT = "INTERRUPT"
    KILLING_BLOW = "KILLING_BLOW"
    KNOCKBACK = "KNOCKBACK"
    NO_LOCATION_FOUND = "NO_LOCATION_FOUND"
    OFFBALANCE = "OFFBALANCE"
    POWER_DRAIN = "POWER_DRAIN"
    POWER_ENERGIZE = "POWER_ENERGIZE"
    QUEUED = "QUEUED"
    REFLECTED = "REFLECTED"
    RESURRECT = "RESURRECT"
    REINCARNATING = "REINCARNATING"
    ROOTED = "ROOTED"
    SNARED = "SNARED"
    SOUL_GEM_RESURRECTION_ACCEPTED = "SOUL_GEM_RESURRECTION_ACCEPTED"
    SPRINTING = "SPRINTING"
    STAGGERED = "STAGGERED"
    STUNNED = "STUNNED"
    TARGET_DEAD = "TARGET_DEAD"
    TARGET_NOT_IN_VIEW = "TARGET_NOT_IN_VIEW"
    TARGET_OUT_OF_RANGE = "TARGET_OUT_OF_RANGE"


class DamageType(Enum):
    BLEED = "BLEED"
    COLD = "COLD"
    DISEASE = "DISEASE"
    FIRE = "FIRE"
    GENERIC = "GENERIC"
    INVALID = "INVALID"
    MAGIC = "MAGIC"
    NONE = "NONE"
    OBLIVION = "OBLIVION"
    PHYSICAL = "PHYSICAL"
    POISON = "POISON"
    SHOCK = "SHOCK"


class ResourceType(Enum):
    UNKNOWN0 = "0"  # Possibly Shield/Absorption
    MAGICKA = "1"
    STAMINA = "4"
    MAGICKA_AND_STAMINA = "5"  # Only triggered by Molten Whip, so probably mixed cost
    ULTIMATE = "8"


class BooleanType(Enum):
    TRUE = "T"
    FALSE = "F"
