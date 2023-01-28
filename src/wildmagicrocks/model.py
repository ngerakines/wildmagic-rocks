from typing import Any, List, Set, Dict, Optional, Tuple
from string import Formatter
from enum import Flag, auto
import numpy
from fnvhash import fnv1a_64

from wildmagicrocks.util import RecursiveFormatter


STATS = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]


class Tags(Flag):
    MINOR = auto()
    MODERATE = auto()
    MAJOR = auto()


def random_duration(rng: numpy.random.Generator, duration_range: Optional[int] = None) -> str:
    if duration_range is None:
        duration_range = rng.integers(1, 100)
    plurality = ""
    if duration_range == 100:
        days = rng.integers(1, 7)
        if days > 1:
            plurality = "s"
        return f"{days} day{plurality}"
    elif duration_range > 50:
        hours = rng.choice([1, 2, 3, 4, 6, 10, 12, 24])
        if hours > 1:
            plurality = "s"
        return f"{hours} hour{plurality}"
    minutes = rng.choice([1, 2, 3, 4, 5, 10, 20, 30, 60])
    if minutes > 1:
        plurality = "s"
    return f"{minutes} minute{plurality}"


TARGETS: List[Tuple[str, bool]] = [
    ("you", False),
    ("you and a random ally", False),
    ("a random ally", True),
    ("an ally you choose", True),
    ("you and an ally you choose", False),
    ("a random enemy", True),
    ("an enemy you choose", True),
    ("a random creature", True),
    ("a creature you choose", True),
    ("all allies", False),
    ("you and your allies", False),
    ("all enemies", False),
    ("all creatures", False),
    ("all other creatures", False),
]

SINGLE_TARGET: List[Tuple[str, bool]] = [
    ("you", False),
    ("a random ally", True),
    ("an ally you choose", True),
    ("a random enemy", True),
    ("an enemy you choose", True),
    ("a random creature", True),
    ("a creature you choose", True),
]

OTHER_SINGLE_TARGET: List[Tuple[str, bool]] = [
    ("a random ally", True),
    ("an ally you choose", True),
    ("a random enemy", True),
    ("an enemy you choose", True),
    ("a random creature", True),
    ("a creature you choose", True),
]

OTHER_TARGETS: List[Tuple[str, bool]] = [
    ("a random ally", True),
    ("an ally you choose", True),
    ("a random enemy", True),
    ("an enemy you choose", True),
    ("a random creature", True),
    ("a creature you choose", True),
    ("all allies", False),
    ("all enemies", False),
    ("all other creatures", False),
]

FRIENDLY_TARGETS: List[Tuple[str, bool]] = [
    ("you", False),
    ("a random ally", True),
    ("an ally you choose", True),
    ("all allies", False),
    ("you and your allies", False),
    ("all friendly creatures", False),
    ("all other friendly creatures", False),
]

TARGET_SCOPES: List[str] = [
    "in your line of sight",
    "within {target_scope_within_feet} feet",
    "in your line of sight within {target_scope_within_feet} feet",
]


def random_target(rng: numpy.random.Generator, targets: List[str] = TARGETS, suffix: Optional[Tuple[str, str]] = None) -> str:
    target, plural = rng.choice(targets)
    if target == "you":
        if suffix is None:
            return target
        return f"{target} {suffix[1]}"

    target_scope = rng.choice(TARGET_SCOPES)

    target_parts = [target, target_scope]
    if suffix is None:
        return " ".join(target_parts)

    return " ".join(target_parts + [suffix[0] if plural else suffix[1]])


class Surge:
    def __init__(self, message: str, values: Dict[str, Any] = {}) -> None:
        self._message = message
        self._message_fields = sorted(list(filter(None, set([v[1] for v in Formatter().parse(self._message)]))))

    def __hash__(self):
        return fnv1a_64(self._message.encode("utf8"))

    def __eq__(self, other):
        if isinstance(other, Surge):
            return self._message == other._message
        return NotImplemented

    def __repr__(self) -> str:
        return hex(self.__hash__())

    def render(self, seed: int) -> str:
        placeholders: Dict[str, str] = {}
        for message_field in self._message_fields:
            rng = numpy.random.default_rng(seed)
            if message_field == "duration":
                placeholders[message_field] = random_duration(rng)
            elif message_field == "duration_minutes":
                placeholders[message_field] = random_duration(rng, duration_range=1)
            elif message_field == "duration_hours":
                placeholders[message_field] = random_duration(rng, duration_range=51)
            elif message_field == "duration_days":
                placeholders[message_field] = random_duration(rng, duration_range=99)
            elif message_field == "change_direction":
                placeholders[message_field] = rng.choice(["increases", "decreases"])
            elif message_field == "simple_color":
                placeholders[message_field] = rng.choice(["red", "green", "blue", "brown", "yellow", "purple"])
            elif message_field == "metal":
                placeholders[message_field] = rng.choice(["iron", "gold", "silver", "bronze", "copper", "steel"])
            elif message_field == "currency":
                placeholders[message_field] = rng.choice(["platinum", "gold", "silver"])
            elif message_field == "element":
                placeholders[message_field] = rng.choice(["fire", "force"])
            elif message_field == "damage_type":
                placeholders[message_field] = rng.choice(
                    [
                        "acid",
                        "bludgeoning",
                        "cold",
                        "fire",
                        "force",
                        "lightning",
                        "necrotic",
                        "piercing",
                        "poison",
                        "psychic",
                        "radiant",
                        "slashing",
                        "thunder",
                    ]
                )
            elif message_field == "sense":
                placeholders[message_field] = rng.choice(["hear", "see", "taste", "smell"])
            elif message_field == "dice_type":
                placeholders[message_field] = rng.choice([2, 4, 6, 8, 10, 12, 20])
            elif message_field == "lose_gain":
                placeholders[message_field] = rng.choice(["lose", "gain"])
            elif message_field == "allies_enemies":
                placeholders[message_field] = rng.choice(["allies", "enemies"])
            elif message_field == "allies_creatures_enemies":
                placeholders[message_field] = rng.choice(["allies", "creatures", "enemies"])
            elif message_field == "one_all":
                placeholders[message_field] = rng.choice(["one", "all"])
            elif message_field == "fives_25":
                placeholders[message_field] = rng.choice([5, 10, 15, 20, 25])
            elif message_field == "tens_20":
                placeholders[message_field] = rng.choice([10, 20])
            elif message_field == "tens_30":
                placeholders[message_field] = rng.choice([10, 20, 30])
            elif message_field == "stat":
                placeholders[message_field] = rng.choice(STATS)
            elif message_field == "low_spell_level":
                placeholders[message_field] = rng.choice(["1st", "2nd", "3rd", "4th", "5th"])
            elif message_field == "ones_2":
                placeholders[message_field] = rng.integers(1, 2)
            elif message_field == "ones_5":
                placeholders[message_field] = rng.integers(1, 5)
            elif message_field == "ones_10":
                placeholders[message_field] = rng.integers(1, 10)
            elif message_field == "createure_type":
                placeholders[message_field] = rng.choice(
                    [
                        "aberrations",
                        "beasts",
                        "celestials",
                        "constructs",
                        "dragons",
                        "elementals",
                        "fey",
                        "fiends",
                        "giants",
                        "humanoids",
                        "monstrosities",
                        "oozes",
                        "plants",
                        "undead",
                    ]
                )
            elif message_field == "gain_target":
                placeholders[message_field] = random_target(rng, suffix=("gains", "gain"))
            elif message_field == "lose_target":
                placeholders[message_field] = random_target(rng, suffix=("loses", "lose"))
            elif message_field == "target_heals":
                placeholders[message_field] = random_target(rng, suffix=("heals", "heal"))
            elif message_field == "target":
                placeholders[message_field] = random_target(rng)
            elif message_field == "other_target":
                placeholders[message_field] = random_target(rng, targets=OTHER_TARGETS)
            elif message_field == "single_target":
                placeholders[message_field] = random_target(rng, targets=SINGLE_TARGET)
            elif message_field == "other_single_target":
                placeholders[message_field] = random_target(rng, targets=OTHER_SINGLE_TARGET)
            elif message_field == "beneficial_target_gains":
                placeholders[message_field] = random_target(rng, targets=FRIENDLY_TARGETS, suffix=("gains", "gain"))

        target_scope_rng = numpy.random.default_rng(seed)
        placeholders["target_scope_within_feet"] = target_scope_rng.choice([10, 20, 30])
        return RecursiveFormatter().format(self._message, **placeholders)

class SurgeIndex:
    def __init__(self, surge_sources: List[str]) -> None:
        self._surges: Dict[str, Surge] = {}

        for source in surge_sources:
            with open(source, "r", encoding="utf-8") as source_file:
                for line in source_file.readlines():
                    surge = Surge(line)
                    self._surges[repr(surge)] = surge

    def random_surges(self, seed: int, count: int = 5) -> List[Tuple[str, str]]:
        if count < 5:
            count = 20
        if count > 100:
            count = 100

        surge_ids: List[str] = list(self._surges.keys())

        rng = numpy.random.default_rng(seed)
        surges: Set[Surge] = set()
        attempts = 0
        while attempts < count * 2 and len(surges) < count:
            attempts += 1
            surge_id = rng.choice(surge_ids)
            surges.add(self._surges[surge_id])

        return [(surge.render(seed).capitalize(), repr(surge)) for surge in sorted(surges, key=lambda x: hash(x))]

    def find_surge(self, seed: int, surge_id: str, raw: bool = False) -> Optional[Tuple[str, str]]:
        surge: Optional[Surge] = self._surges.get(surge_id, None)
        if surge is None:
            return None
        if raw:
            return surge._message, repr(surge)
        return surge.render(seed).capitalize(), repr(surge)
