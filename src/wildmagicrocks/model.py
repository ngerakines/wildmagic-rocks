from typing import Any, FrozenSet, List, Sequence, Set, Dict, Optional, Tuple
from string import Formatter
import numpy
from fnvhash import fnv1a_64

from wildmagicrocks.util import RecursiveFormatter


STATS = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]

duration_weights = (["minute", "hour", "day"], [30, 15, 1])

duration_values = {
    "minute": ([1, 2, 3, 4, 5, 10, 15, 20, 30], [200, 100, 150, 100, 50, 40, 30, 20, 10]),
    "hour": ([1, 2, 3, 6, 10, 12, 24], [200, 100, 20, 15, 10, 5, 1]),
    "day": ([1, 2, 3, 5, 7, 14], [300, 150, 75, 25, 10, 1]),
}


def random_duration(rng: numpy.random.Generator, duration_type: Optional[str] = None) -> str:
    if duration_type is None:
        weights = numpy.array(duration_weights[1], dtype=numpy.float64)
        weights /= weights.sum()
        duration_type = rng.choice(duration_weights[0], p=weights)

    values = duration_values[duration_type][0]

    weights = numpy.array(duration_values[duration_type][1], dtype=numpy.float64)
    weights /= weights.sum()

    value = rng.choice(values, p=weights)
    plurality = ""
    if value > 1:
        plurality = "s"

    return f"{value} {duration_type}{plurality}"


TARGETS: List[Tuple[str, bool, int]] = [
    ("you", False, 100),
    ("you and a random ally", False, 5),
    ("a random ally", True, 50),
    ("an ally you choose", True, 50),
    ("you and an ally you choose", False, 5),
    ("a random enemy", True, 50),
    ("an enemy you choose", True, 25),
    ("a random creature", True, 25),
    ("a creature you choose", True, 25),
    ("all allies", False, 50),
    ("you and your allies", False, 50),
    ("all enemies", False, 25),
    ("all creatures", False, 25),
    ("all other creatures", False, 25),
]

SINGLE_TARGET: List[Tuple[str, bool, int]] = [
    ("you", False, 1),
    ("a random ally", True, 1),
    ("an ally you choose", True, 1),
    ("a random enemy", True, 1),
    ("an enemy you choose", True, 1),
    ("a random creature", True, 1),
    ("a creature you choose", True, 1),
]

OTHER_SINGLE_TARGET: List[Tuple[str, bool, int]] = [
    ("a random ally", True, 1),
    ("an ally you choose", True, 1),
    ("a random enemy", True, 1),
    ("an enemy you choose", True, 1),
    ("a random creature", True, 1),
    ("a creature you choose", True, 1),
]

OTHER_TARGETS: List[Tuple[str, bool, int]] = [
    ("a random ally", True, 1),
    ("an ally you choose", True, 1),
    ("a random enemy", True, 1),
    ("an enemy you choose", True, 1),
    ("a random creature", True, 1),
    ("a creature you choose", True, 1),
    ("all allies", False, 1),
    ("all enemies", False, 1),
    ("all other creatures", False, 1),
]

FRIENDLY_TARGETS: List[Tuple[str, bool, int]] = [
    ("you", False, 1),
    ("a random ally", True, 1),
    ("an ally you choose", True, 1),
    ("all allies", False, 1),
    ("you and your allies", False, 1),
    ("all friendly creatures", False, 1),
    ("all other friendly creatures", False, 1),
]

FRIENDLY_SINGLE_TARGETS: List[Tuple[str, bool, int]] = [
    ("you", False, 1),
    ("a random ally", True, 1),
    ("an ally you choose", True, 1),
    ("all allies", False, 1),
    ("you and your allies", False, 1),
    ("all friendly creatures", False, 1),
    ("all other friendly creatures", False, 1),
]

TARGET_SCOPES: List[Tuple[str, int]] = [
    ("", 4),
    ("in your line of sight", 3),
    ("within {target_scope_within_feet} feet", 2),
    ("in your line of sight within {target_scope_within_feet} feet", 1),
]


def random_target(
    rng: numpy.random.Generator,
    targets: List[Tuple[str, bool, int]] = TARGETS,
    suffix: Optional[Tuple[str, str]] = None,
) -> str:
    target_weights = numpy.array([weight for (_, _, weight) in targets], dtype=numpy.float64)
    target_weights /= target_weights.sum()
    target, plural = rng.choice(
        [(target_value, target_plural) for (target_value, target_plural, _) in targets], p=target_weights
    )

    if target == "you":
        if suffix is None:
            return target
        return f"{target} {suffix[1]}"

    target_scope_weights = numpy.array([weight for (_, weight) in TARGET_SCOPES], dtype=numpy.float64)
    target_scope_weights /= target_scope_weights.sum()
    target_scope = rng.choice([target_scope_value for (target_scope_value, _) in TARGET_SCOPES], p=target_scope_weights)

    target_parts = [target]
    if len(str(target_scope)) > 0:
        target_parts.append(target_scope)
    if suffix is None:
        return " ".join(target_parts)

    return " ".join(target_parts + [suffix[0] if plural else suffix[1]])


def split_message_tags(line: str) -> Tuple[str, List[str]]:
    if "|" not in line:
        return line, expand_tags(line, [])
    message, tag_list = line.split("|", 1)
    return message, expand_tags(message, tag_list.split(","))


def expand_tags(message: str, tags: Sequence[str]) -> FrozenSet[str]:
    results: Set[str] = set()

    for tag in tags:
        tag = tag.strip().lower()
        if len(tag) > 0:
            results.add(tag)

    if "heals" in message:
        results.add("healing")
    if "immediately heal" in message:
        results.add("healing")
    if "{duration}" in message:
        results.add("minutes")
        results.add("hours")
        results.add("days")
    if "{duration_minutes}" in message:
        results.add("minutes")
    if "{duration_hours}" in message:
        results.add("hours")
    if "{duration_days}" in message:
        results.add("days")
    if "item in your possession" in message:
        results.add("object")

    return frozenset(results)


class Surge:
    def __init__(self, message: str) -> None:
        self._message, self._tags = split_message_tags(message)
        self._message_fields = sorted(
            list(filter(None, set([v[1] for v in Formatter().parse(self._message)] + ["target_scope_within_feet"])))
        )

    def __hash__(self):
        return fnv1a_64(self._message.encode("utf8"))

    def __eq__(self, other):
        if isinstance(other, Surge):
            return self._message == other._message
        return NotImplemented

    def __repr__(self) -> str:
        return "{:x}".format(self.__hash__())

    def message(self) -> str:
        return self._message

    def all_tags(self) -> Set[str]:
        return frozenset(self._tags)

    def include(self, include_tags: Optional[Set[str]], exclude_tags: Optional[Set[str]]) -> bool:
        if include_tags is not None:
            for include_tag in include_tags:
                if include_tag not in self._tags:
                    return False
        if exclude_tags is not None:
            for exclude_tag in exclude_tags:
                if exclude_tag in self._tags:
                    return False
        return True

    def render(self, seed: int) -> str:
        placeholders: Dict[str, str] = {}
        for message_field in self._message_fields:
            rng = numpy.random.default_rng(seed)
            if message_field == "duration":
                placeholders[message_field] = random_duration(rng)
            elif message_field == "duration_minutes":
                placeholders[message_field] = random_duration(rng, duration_type="minute")
            elif message_field == "duration_hours":
                placeholders[message_field] = random_duration(rng, duration_type="hour")
            elif message_field == "duration_days":
                placeholders[message_field] = random_duration(rng, duration_type="day")
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
            elif message_field == "dragon_type":
                placeholders[message_field] = rng.choice(
                    ["black", "blue", "brass", "bronze", "copper", "gold", "green", "red", "silver", "white"]
                )
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
            # plane
            elif message_field == "plane":
                placeholders[message_field] = rng.choice(
                    [
                        "The Material Plane",
                        "Feywild",
                        "Shadowfell",
                        "The Ethereal Plane",
                        "The Astral Plane",
                        "The Elemental Plane of Air",
                        "The Elemental Plane of Fire",
                        "The Elemental Plane of Earth",
                        "The Elemental Plane of Water",
                        "The Elemental Chaos",
                        "Arcadia",
                        "Mount Celestia",
                        "Bytopia",
                        "Elysium",
                        "The Beastlands",
                        "Arborea",
                        "Ysgard",
                        "Limbo",
                        "Pandemonium",
                        "The Abyss",
                        "Carceri",
                        "Hades",
                        "Gehenna",
                        "The Nine Hells",
                        "Archeron",
                        "Mechanus",
                        "The City of Sigil",
                    ]
                )
            elif message_field == "sense":
                placeholders[message_field] = rng.choice(["hear", "see", "taste", "smell"])
            elif message_field == "dice_type":
                placeholders[message_field] = rng.choice([2, 4, 6, 8, 10, 12, 20])
            elif message_field == "dice_type_low":
                placeholders[message_field] = rng.choice([2, 4, 6])
            elif message_field == "dice_type_high":
                placeholders[message_field] = rng.choice([8, 10, 12, 20])
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
            elif message_field == "left_right":
                placeholders[message_field] = rng.choice(["left", "right"])
            elif message_field == "low_spell_level":
                placeholders[message_field] = rng.choice(["1st", "2nd", "3rd", "4th"])
            elif message_field == "high_spell_level":
                placeholders[message_field] = rng.choice(["5th", "6th", "7th", "8th"])
            elif message_field == "ones_2":
                placeholders[message_field] = rng.integers(1, 2)
            elif message_field == "ones_5":
                placeholders[message_field] = rng.integers(1, 5)
            elif message_field == "ones_10":
                placeholders[message_field] = rng.integers(1, 10)
            elif message_field == "creature_type":
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
            elif message_field == "language":
                placeholders[message_field] = rng.choice(
                    [
                        "common",
                        "dawrven",
                        "elven",
                        "gian",
                        "gnomish",
                        "goblin",
                        "halfling",
                        "orc",
                        "abyssal",
                        "celestial",
                        "draconic",
                        "deep speech",
                        "infernal",
                        "primordial",
                        "sylvan",
                        "undercommon",
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
            elif message_field == "single_target_gains":
                placeholders[message_field] = random_target(rng, targets=SINGLE_TARGET, suffix=("gains", "gain"))
            elif message_field == "other_single_target":
                placeholders[message_field] = random_target(rng, targets=OTHER_SINGLE_TARGET)
            elif message_field == "beneficial_target_gains":
                placeholders[message_field] = random_target(rng, targets=FRIENDLY_TARGETS, suffix=("gains", "gain"))
            elif message_field == "beneficial_single_target_gains":
                placeholders[message_field] = random_target(
                    rng, targets=FRIENDLY_SINGLE_TARGETS, suffix=("gains", "gain")
                )
            elif message_field == "target_scope_within_feet":
                placeholders[message_field] = rng.choice([10, 20, 30])

        return RecursiveFormatter().format(self._message, **placeholders)


class SurgeIndex:
    def __init__(self, surge_sources: List[str]) -> None:
        self._available_tags: Set[str] = set()
        self._surges: Dict[str, Surge] = {}
        for source in surge_sources:
            with open(source, "r", encoding="utf-8") as source_file:
                for line in source_file.readlines():
                    surge = Surge(line)
                    self._surges[repr(surge)] = surge
                    self._available_tags.update(surge.all_tags())
        self._surge_ids: List[str] = list(sorted(set(self._surges.keys())))

    def all_filters(self) -> Set[str]:
        return self._available_tags

    def export(self) -> List[Tuple[str, str, Set[str]]]:
        results: List[Tuple[str, str, Set[str]]] = []
        for (surge_id, surge) in self._surges.items():
            results.append((surge_id, surge.message(), surge.all_tags()))
        return results

    def random_surges(
        self,
        seed: int,
        count: int = 5,
        include_tags: Optional[Set[str]] = None,
        exclude_tags: Optional[Set[str]] = None,
    ) -> List[Tuple[str, str]]:
        if count < 0:
            count = 1
        if count > 100:
            count = 100

        if include_tags is not None:
            include_diff = include_tags.difference(self._available_tags)
            if len(include_diff) > 0:
                return []
        if exclude_tags is not None:
            exclude_diff = exclude_tags.difference(self._available_tags)
            if len(exclude_diff) > 0:
                return []

        surge_ids: List[str] = self._surge_ids.copy()
        if include_tags is not None or exclude_tags is not None:
            surge_ids.clear()
            for (surge_id, surge) in self._surges.items():
                if surge.include(include_tags=include_tags, exclude_tags=exclude_tags):
                    surge_ids.append(surge_id)

        if len(surge_ids) == 0:
            return []

        rng = numpy.random.default_rng(seed)
        surges: List[Surge] = []
        attempts = 0
        while len(surges) < count and attempts < count * 2:
            attempts += 1
            surge_id = rng.choice(surge_ids)
            surges.append(self._surges[surge_id])

        return [(self.normalize(surge.render(seed)), repr(surge)) for surge in sorted(surges, key=lambda x: hash(x))]

    def find_surge(self, seed: int, surge_id: str, raw: bool = False) -> Optional[Tuple[str, str]]:
        surge: Optional[Surge] = self._surges.get(surge_id, None)
        if surge is None:
            return None
        if raw:
            return surge._message, repr(surge)
        return self.normalize(surge.render(seed)), repr(surge)

    def normalize(self, message: str) -> str:
        # Nick: This is ugly. I know.
        values: List[str] = []
        for sent in message.split("."):
            sent = sent.strip().removesuffix(".").strip()
            if len(sent) == 0:
                continue
            words = sent.split(" ")
            values.append(words[0].title() + " " + " ".join(words[1:]) + ".")
        return " ".join(values)
