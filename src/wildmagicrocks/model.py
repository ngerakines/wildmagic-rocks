from typing import Any, List, Set, Dict, Optional, Tuple
from string import Formatter
from enum import Flag, auto
import numpy
from fnvhash import fnv1a_64


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


def random_target(rng: numpy.random.Generator, suffix: Optional[str] = None) -> str:
    target = rng.choice(
        [
            "you",
            "a random ally in your line of sight",
            "all allies in your line of sight",
            "you and your allies in your line of sight",
            "a random target in your line of sight",
            "a target of your choice in your line of sight",
            "you and all creatures in your line of sight",
            "all other creatures in your line of sight",
        ]
    )
    if suffix is not None:
        return f"{target} {suffix}"
    return target


def random_other_target(rng: numpy.random.Generator, suffix: Optional[str] = None) -> str:
    target = rng.choice(
        [
            "a random ally in your line of sight",
            "all allies in your line of sight",
            "a random target in your line of sight",
            "a target of your choice in your line of sight",
            "all other creatures in your line of sight",
        ]
    )
    if suffix is not None:
        return f"{target} {suffix}"
    return target


def random_beneficial_target(rng: numpy.random.Generator, suffix: Optional[str] = None) -> str:
    target = rng.choice(["you", "a random ally in your line of sight", "an ally of your choice in your line of sight", "all allies in your line of sight", "you and your allies in your line of sight"])
    if suffix is not None:
        return f"{target} {suffix}"
    return target


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
                placeholders[message_field] = random_target(rng, "gains")
            elif message_field == "target":
                placeholders[message_field] = random_target(rng)
            elif message_field == "other_target":
                placeholders[message_field] = random_other_target(rng)
            elif message_field == "beneficial_target_gains":
                placeholders[message_field] = random_beneficial_target(rng, "gains")
        return Formatter().format(self._message, **placeholders)


class TempStatChangeSurge(Surge):
    def render(self, seed: int) -> str:
        rng = numpy.random.default_rng(seed)
        return self._message.format(
            stat=rng.choice(STATS),
            change_direction=rng.choice(["increases", "decreases"]),
            amount=rng.choice([1, 2]),
            duration=random_duration(rng, duration_range=99),
        )


class PermStatChangeSurge((Surge)):
    def render(self, seed: int) -> str:
        rng = numpy.random.default_rng(seed)
        return self._message.format(
            stat=rng.choice(STATS),
            change_direction=rng.choice(["increases", "decreases"]),
            amount=rng.choice([1, 2]),
        )


SURGES = [
    # Wealth
    Surge("{ones_5}d{dice_type} {currency} pieces appear near you."),
    Surge("3d{dice_type} random gems appear near you, worth 50gp each."),
    Surge("A 30-foot cube hypnotic pattern appears with you at the center. All creatures within the pattern must succeed on a Wisdom saving throw or fall asleep for 1 minute or until they take damage."),
    Surge(
        "A fireball explodes with you at the center. You and each creature within 20 feet must make a Dexterity saving throw using your spell save DC, taking 5d6 fire damage on a failed save, or half as much damage on a successful one."
    ),
    Surge("A gentle gust of wind blows outward from you. All creatures within 40 feet of you can feel it, but it otherwise does nothing."),
    Surge("A loud boom emanates from you. All creatures within 15 feet take 2d8 thunder damage and must make a Constitution saving throw against your spell save DC or be deafened for {duration_minutes}."),
    Surge("A magic mouth appears on a nearby wall or flat surface. When you speak, your voice comes from the magic mouth. This lasts for {duration_minutes}."),
    Surge("A puddle of grease appears where you are standing, with a 10-foot radius. You and anyone within 10 feet of you must make a Dexterity check at your spell save DC or fall prone."),
    Surge("A random creature within 60 feet of you is poisoned for {duration_hours}."),
    Surge("A third eye appears in your forehead, giving you advantage on sight-based Wisdom (Perception) checks for 1 minute."),
    Surge("All {allies_creatures_enemies} within your line of sight {lose_gain} {ones_2} to attack and damage rolls for any ranged attack they make within the next {duration_minutes}."),
    Surge("All {allies_creatures_enemies} within {tens_30} feet of you {lose_gain} {ones_2} to attack and damage rolls for any ranged attack they make within the next {duration_minutes}."),
    Surge("All {allies_creatures_enemies} within your line of sight {lose_gain} {ones_2} to attack and damage rolls for any melee attack they make within the next {duration_minutes}."),
    Surge("All {allies_creatures_enemies} within {tens_30} feet of you {lose_gain} {ones_2} to attack and damage rolls for any melee attack they make within the next {duration_minutes}."),
    Surge("All {allies_creatures_enemies} within your line of sight heal up to {ones_5}d{dice_type} hit points."),
    Surge("All {allies_creatures_enemies} within {tens_30} feet of you heal up to {ones_5}d{dice_type} hit points."),
    Surge("All {allies_creatures_enemies} within your line of sight must make a Wisdom saving throw against your spell save DC or be frightened of you."),
    Surge("All {allies_creatures_enemies} within {tens_30} feet of you must make a Wisdom saving throw against your spell save DC or be frightened of you."),
    Surge("All {allies_creatures_enemies} within your line of sight must make a Strength saving throw against your spell save DC or be knocked prone."),
    Surge("All {allies_creatures_enemies} within {tens_30} feet of you must make a Strength saving throw against your spell save DC or be knocked prone."),
    Surge("All of your non-magical clothing and equipment teleports to the nearest open space at least 15 feet from you that you can see."),
    Surge("All spells that {allies_creatures_enemies} cast within the next minute automatically fail."),
    Surge(
        "An creature of your CR of the DM's choosing appears within {tens_30} feet of you. Make a Charisma saving throw against your spell save DC. If you succeed it, the creature is subservient, otherwise, it is hostile. The creature, if not banished or defeated, vanishes after {duration_days}."
    ),
    Surge("Choose 1 permanent or triggered effect that has happened to you or somebody else that you've received from a wild magic surge and remove it, even if it was beneficial."),
    Surge("During the next hour, you may re-roll any one save, attack roll, or skill check. If you do, you must take the new roll's result."),
    Surge("All {allies_creatures_enemies} within your line of sight takes {ones_5}d{dice_type} necrotic damage. You regain hit points equal to the sum of damage dealt."),
    Surge("Every inanimate object that isn't being worn or carried within 40 feet of you becomes enshrouded with shadows for 1 minute. Enshrouded objects are considered heavily obscured."),
    Surge(
        "A duplicate of yourself appears in the nearest open space which can take actions independently, and goes on the same Initiative as you. However, any damage it takes as well as any spell slots or sorcery point it uses applies to you as well. This lasts {duration_minutes}."
    ),
    Surge("Any flammable item you touch, that you aren't already wearing or carrying, bursts into flame. This lasts {duration_minutes}."),
    Surge("{gain_target} a {ones_2} penalty to attack rolls, damage rolls, and their AC."),
    Surge("You glow bright {simple_color}. You have disadvantage on Stealth checks and anyone trying to perceive you has advantage on their Perception check. This lasts {duration_hours}."),
    Surge("You have a faint {simple_color} glow. Anyone trying to perceive you has advantage on their Perception check. This lasts {duration_hours}."),
    Surge("The next spell that you cast within {duration_minutes} that requires a saving throw, the target gains advantage."),
    Surge("The next spell that you cast within {duration_minutes} with a casting time of 1 action can be cast as a bonus action."),
    Surge("The next ability check that you make within {duration_hours}, roll 1d{dice_type} and add the result."),
    Surge("The next ability check that you make within {duration_hours}, roll 1d{dice_type} and subtract the result."),
    Surge("you are unable to read as the letters all appeared jumbled. This effect lasts {duration}."),
    Surge("You gain advantage on {stat} checks when dealing with any creature wearing {simple_color}, but disadvantage if they are wearing not."),
    Surge("All attacks you make with a non-magical weapon gain a +1 bonus to hit and to damage, and are considered magical for the purpose of overcoming resistances. This lasts {duration}."),
    Surge("All spells with a casting time of 1 action or 1 bonus action require 2 consecutive actions to cast. This lasts {duration}."),
    Surge("Any creature you touch takes 1d{dice_type} lightning damage. This lasts {duration}."),
    Surge("Every creature within {tens_30} feet of you that hears you speak only hears insults as if you are casting vicious mockery at first level. This lasts {duration}."),
    Surge("You are unable to cast any spell that causes damage of any type. This effect lasts {duration}."),
    Surge("You can pass through any solid, non-magical wall that is 6 or fewer inches thick. This effect lasts {duration}."),
    Surge("You can teleport up to 20 feet as part of your movement on each of your turns, for {duration_minutes}."),
    Surge("You have double vision. This gives you disadvantage on ranged attacks (including spell attacks) and Perception checks involving sight. This effect lasts {duration}."),
    Surge("You must shout when you speak for {duration}."),
    Surge("You must whisper when you speak for {duration}."),
    Surge("You may not speak unless you are stepping, for {duration}."),
    Surge("You may not speak unless you are dancing, for {duration}."),
    Surge("The next spell you cast that does damage, the effect is minimized."),
    Surge("The next spell you cast that does damage, the effect is maximized."),
    Surge("If you cast a spell with a saving throw within the next minute, the target gains disadvantage on its saving throw."),
    Surge("Illusory butterflies and flower petals flutter in the air around you in a 10-foot radius for {duration}."),
    Surge("{target} must Constitution saving throw against your spell save DC. If you fail, they are stunned for {duration_minutes}."),
    Surge("You are transformed into a different gender (if possible) of your current creature type, as if by the polymorph spell."),
    Surge("Make a Wisdom saving throw against your spell save DC. If you fail, you are transformed into a beast of your CR from your current plane for {duration_minutes}, as if by the polymorph spell."),
    Surge("Make a Wisdom saving throw against your spell save DC. If you fail, you are transformed into a non-intelligent small-medium size creature for {duration_minutes}, as if by the polymorph spell."),
    Surge("Make a Wisdom saving throw against your spell save DC. If you fail, you are transformed into a sheep for {duration_minutes}, as if by the polymorph spell."),
    Surge("Make a Wisdom saving throw against your spell save DC. If you fail, you are transformed into a creature type in your line of sight at random for {duration_minutes}, as if by the polymorph spell."),
    Surge(
        "Make a Wisdom saving throw against your spell save DC. If you fail, you are transformed into a creature type of your choosing in your line of sight for {duration_minutes}, as if by the polymorph spell."
    ),
    Surge(
        "Mushrooms sprout around you in a 5-foot radius and vanish after 1 minute. If one is harvested and eaten within this time, the creature must make a Constitution saving throw against your spell save DC. On a failed save, it takes 5d{dice_type} poison damage. On successful one, it gains 5d{dice_type} temporary hit points."
    ),
    # Items
    Surge("One non-magical item in your possession becomes magical."),
    Surge("All non-magical items within 10 feet are repaired as if you cast Mending."),
    Surge("The Create Water effect occurs at the discression of the DM as if you cast Create or Destroy Water."),
    Surge("The Destroy Water effect occurs at the discression of the DM as if you cast Create or Destroy Water."),
    Surge("All non-magical food and drink is effected as if you cast Purify Food and Drink."),
    Surge("A rope in your position or with 10 feet of you is effected as if you cast Rope Trick for {duration_hours}."),
    Surge("Over the {duration_minutes}, all plants within 20 feet of you grow as if affected by the plant growth spell."),
    Surge("One randomly-chosen non-magical item in your possession that weighs 1 pound or less is duplicated."),
    Surge("One randomly-chosen non-magical item in your possession that weighs 1 pound or less vanishes and is forever gone."),
    Surge("The caster learns the location of the nearest legendary magical item, either through a brief vision of it's location or an approximate distance from their current whereabouts."),
    Surge("The caster learns the location of the nearest sentient magical item, either through a brief vision of it's location or an approximate distance from their current whereabouts."),
    Surge("The next creature that dies within the next minute within 30 feet, comes back to life as if you cast ressurection. It believes that you are it's diety."),
    Surge("The next time you fall below 0 hit points within the next month, you automatically fail your first death saving throw."),
    Surge("Up to three creatures you choose within 30 feet of you take 1d{dice_type} lightning damage equal to your level."),
    Surge("{target} takes 1d{dice_type} {damage_type} damage."),
    Surge("{target} takes 2d{dice_type} {damage_type} damage."),
    Surge("{target} takes 3d{dice_type} {damage_type} damage."),
    Surge("All creatures within 10 feet of you take 5d{dice_type} {damage_type} damage distributed evenly"),
    Surge("All creatures within 30 feet of you take 10d{dice_type} {damage_type} damage distributed evenly"),
    Surge("{gain_target} vulnerability to {damage_type} damage for {duration_minutes}."),
    Surge("{gain_target} resistance to {damage_type} damage for {duration_minutes}."),
    Surge("{gain_target} resistance to all damage types for {duration_minutes}."),
    Surge("You are at the center of a 10-foot radius antimagic field that negates all magic equal to or less than your level for {duration_hours} and does not require concentration."),
    Surge("You are at the center of a Darkness spell as if you cast it for {duration_minutes}."),
    Surge("You are at the center of a Fog Cloud spell as if you cast it for {duration_minutes}."),
    Surge("You are immune to disease for {duration_days}."),
    Surge("You are immune to intoxication for {duration_days}."),
    Surge("You are protected from {createure_type} for {duration}. Such creatures cannot attack you or harm you unless they save a Charisma saving throw against your spell save DC."),
    Surge("You are vulnerable to {createure_type} for {duration}. Such creatures gain advantage when attacking you."),
    Surge("You gain advantage against all {createure_type} for {duration}."),
    Surge("You gain advantage against all {damage_type} damage for {duration}."),
    Surge("You become intoxicated for {duration_hours}."),
    Surge("You die and after 30 seconds True Ressurection is immediately cast on you by an available diety of the player's choosing. "),
    Surge("You emanate light in a 30-foot radius for {duration_minutes}. Any creature within 5 feet of you that can see is blinded until the end of its next."),
    # Skills and proficiency
    Surge("You gain proficiency in all {stat} checks for the next hour"),
    Surge("You gain proficiency in one skill of your choice that you're not already proficient in for {duration}."),
    Surge("You gain proficiency in one tool or weapon type of your choice that you're not already proficient in for {duration}."),
    Surge("You gain the ability to speak one additional language of your choice for {duration}."),
    Surge("You loose the ability to speak a random language you know for {duration}."),
    # Spell effects and abilities
    Surge("{gain_target} the ability to speak with animals for {duration}."),
    Surge("{gain_target} the ability to walk on water for {duration}."),
    Surge("{gain_target} the ability to breathe under water for {duration}."),
    Surge("{gain_target} the effect of Cure Wounds as if you cast it."),
    Surge("You and your allies gain the effect of Mass Cure Wounds as if you cast it."),
    Surge("{beneficial_target_gains} the effect of Protection from Poison for {duration}."),
    Surge("{beneficial_target_gains} the effect of Protection from Energy for {duration}."),
    Surge("{beneficial_target_gains} the effect of Protection from Evil and Good for {duration}."),
    Surge("{gain_target} the effect of Expeditious Retreat for {duration_minutes}."),
    Surge("{gain_target} the effect of Death Ward for {duration}."),
    Surge("{gain_target} the effect of Detect Magic for {duration}."),
    Surge("{gain_target} the effect of Enlarge as part of Enlarge/Reduce for {duration}."),
    Surge("{gain_target} the effect of Reduce as part of Enlarge/Reduce for {duration}."),
    Surge("{gain_target} the effect of Detect Evil and Good for {duration}."),
    Surge("{gain_target} the effect of Detect Poison and Disease for {duration}."),
    Surge("{gain_target} the effect of Detect Thoughts for {duration}."),
    Surge("{gain_target} the effect of Spider Climb for {duration}."),
    Surge("{gain_target} the effect of Faerie Fire for {duration}."),
    Surge("You gain the effect of Antipathy of Antipathy/Sympathy for {duration}."),
    Surge("You gain the effect of Sympathy of Antipathy/Sympathy for {duration}."),
    Surge("{gain_target} the effect of Sleep for {duration_minutes}."),
    Surge("{gain_target} the effect of Blur for {duration}."),
    Surge("{gain_target} the effect of Blink for {duration_minutes}."),
    Surge("{gain_target} the effect of Slow for {duration_minutes}."),
    Surge("{gain_target} the effect of Confusion for {duration_minutes}."),
    Surge("{gain_target} the effect of Shield for {duration}."),
    Surge("{gain_target} the effect of Silence for {duration_minutes}."),
    Surge("{gain_target} the effect of Invisibility and Silence for {duration_minutes}. The effect ends for a target that attacks, or casts a spell."),
    Surge("{gain_target} the effect of Freedom of Movement for {duration}."),
    Surge("{gain_target} the effect of Blindsight with a radius of 60 feet for {duration}."),
    Surge("{gain_target} the effect of Darkvision with a radius of 60 feet for {duration}."),
    Surge("{gain_target} the effect of Fly for {duration}."),
    Surge("{gain_target} the effect of Feather Fall for {duration}."),
    Surge("{gain_target} the effect of Levitate for {duration}."),
    Surge("{gain_target} the effect of Mirror Image for {duration}."),
    Surge("{gain_target} the service of a {low_spell_level}-level spirital weapon for {duration_minutes}."),
    Surge("{gain_target} the service of a phantom steed for {duration}."),
    Surge("{gain_target} the service of an arcane eye for {duration}."),
    Surge("{gain_target} the service of an arcane sword for {duration}."),
    Surge("{gain_target} the service of an unseen servant for {duration}."),
    Surge("{gain_target} the effect of tremorsense with a range of 30 feet for {duration}."),
    # Senses
    Surge("You lose the ability to {sense} for {duration}."),
    Surge("You permanently lose the ability to {sense}. This sense can be restored with a spell that removes curses such as remove curse."),
    # Skill rolls
    Surge("You lose proficiency in all skill rolls for {duration}."),
    Surge("You {lose_gain} proficiency in one randomly chosen skill, tool, or weapon type for 2d6 days."),
    # Combat
    Surge("You gain a -2 penalty to your AC for 1 minute."),
    Surge("You gain a +1 to your AC for one minute."),
    Surge("You gain a +2 bonus to your AC for 1 minute."),
    Surge("You get gain a -1 penalty to your AC for 1 minute."),
    # Health
    Surge("You immediately drop to 0 hit points."),
    Surge("You immediately drop to 1 hit point."),
    Surge("You immediately gain {fives_25} temporary hit points for {duration}."),
    Surge("You immediately heal 1d{dice_type} hit points."),
    Surge("You immediately heal 2d{dice_type} hit points."),
    Surge("You immediately heal 3d{dice_type} hit points."),
    Surge("You immediately heal 4d{dice_type} hit points."),
    Surge("You immediately heal {fives_25} hit points."),
    Surge("You immediately lose {one_all} unspent sorcery points."),
    Surge("You immediately take 1d{dice_type} {damage_type} damage. This damage does not bring you below 1 hit point."),
    Surge("You immediately take 2d{dice_type} {damage_type} damage. This damage does not bring you below 1 hit point."),
    Surge("You regain 5 hit points per round for {duration_minutes}."),
    # Time
    Surge("You jump forward in time exactly 1 minute, for 1 minute. From the perspective of everyone else, you cease to exist during that time."),
    # Appearance and conditions
    Surge("You {lose_gain} 1d6x4 percent of your weight. You gradually return to your original weight over the course of {duration}."),
    Surge("You make no sounds for {duration_minutes} and you gain advantage on any Dexterity (Stealth) checks."),
    Surge("Your height {change_direction} by 1d6 inches. You gradually return to your original height over the course of {duration}."),
    Surge("You transform into an {metal} statue of yourself for {duration_minutes}, during which time you are considered petrified."),
    Surge("You transform into an small-medium size inanimate object of the DM's choosing. During this time you are petrified. After {duration} you return to normal."),
    Surge("Your eyes glow {simple_color} for {duration}."),
    Surge("Your eyes permanently change color and are now {simple_color}. A spell such as remove curse can end this effect."),
    Surge("Your feet sink into the ground, making you completely immobile for {duration_minutes}. This has no effect if you were not standing on the ground when the spell was cast."),
    Surge("Your fingernails and toenails grow to an uncomfortable length. Until you trim them, your Dexterity is reduced by 1 and your speed is reduced by 5 feet."),
    Surge("Your fingers become sore for {duration}. During this time, you must succeed on a Dexterity saving throw against your spell save DC to cast a spell with a somatic component."),
    Surge("Your skin permanently darkens as if you have a tan, or if you are already dark-skinned, your skin becomes one shade lighter. A spell such as remove curse can end this effect."),
    Surge("Your clothes become dirty and filthy. Until you can change and/or clean your clothes, your Charisma is reduced by 1."),
    Surge("You grow 1d{dice_type} inches in height. You gradually return to your original height over the course of {duration}."),
    Surge("You grow a beard made of feathers, which remains until you sneeze."),
    Surge("Your spell components seem to have been rearranged. For {duration_minutes}, you must make an Intelligence check against your spell save DC to cast any spell that requires a material component."),
    Surge("You have a momentary vision of your own death. If you fail a Wisdom saving roll at your spell DC, you are frightened for {duration_minutes}."),
    Surge(
        "You have the irresistible urge to scratch an itch in the middle your back, just out of reach, for {duration_minutes}. If you don't scratch it using a back scratcher or some similar device , you must succeed a Constitution saving throw against your spell save DC to cast a spell."
    ),
    Surge("You hear a ringing in your ears for {duration_minutes}. During this time, casting a spell that requires a verbal component requires a Constitution check against your spell save DC."),
    Surge("A bad joke comes to mind and until you tell it (which takes an entire action), you suffer a Wisdom penalty of 1."),
    Surge("You can hear exceptionally well for {duration_minutes}, gaining advantage for all Perception checks related to sound."),
    Surge("You can smell exceptionally well for {duration_minutes}, gaining blindsight with a radius of 10 feet and advantage on all Perception checks related to odor."),
    Surge("You fall victim to a horrible cramp in both legs, reducing your speed by 10 feet for {duration_minutes}."),
    Surge("You feel extremely nauseated. Make a Constitution saving throw against your spell save DC. If you fail, you must spend your next action throwing up."),
    Surge("For the next day, each time you say a word with the 's' sound, it sounds like a hissing snake."),
    Surge("You can't speak for {duration_minutes}. When you try, pink bubbles float out of your mouth."),
    Surge("For the next {duration_hours}, your skin tone changes color every 30 minutes, cycling through the colors of the rainbow."),
    Surge("Plants grow around you and you are restrained for 1 minute."),
    Surge("Small birds flutter and chirp in your vicinity for 1 minute, during which time you automatically fail any Stealth check."),
    Surge("You are surrounded by a faint, offensive odor for 1 minute. You gain disadvantage on all Charisma checks."),
    Surge("You are surrounded by a faint, pleasant odor. You gain advantage on all Charisma checks you make within the next minute."),
    Surge("You are surrounded by a horrible, noxious odor for 1 minute. Anyone within 10 feet of you must make a Constitution saving throw or be stunned."),
    # Spell slots and casting
    Surge("You permanently forget one cantrip. A spell such as remove curse can restore your memory."),
    Surge("You permanently gain one 1st-level spell slot but forget one cantrip that you already know. A spell such as remove curse can end this effect."),
    Surge("You permanently gain one cantrip. A spell such as remove curse can end this effect."),
    Surge("You permanently gain one spell slot of one level below your highest-level spell slot, but lose one 1st-level spell slot. A spell such as remove curse can end this effect."),
    Surge("You recover 1 expended spell slot of your choice."),
    Surge("You recover all your expended spell slots."),
    Surge("You recover your lowest-level expended spell slot."),
    Surge("You regain all expended sorcery points."),
    Surge("You gain two spell slots at your second-highest level for 1 week."),
    Surge("You gain an additional spell slot of your highest level for 1 week."),
    Surge("The next single target spell you cast within the next minute must target one additional target."),
    Surge("The next spell you cast within the hour uses a slot level one level higher than what it normally requires."),
    Surge(
        "The next spell you cast within the next hour uses a spell slot of one level lower than what it normally requires. If the spell is a spell of 1st level, you still must expend a spell slot to cast it."
    ),
    Surge("The next spell you cast within the next minute that does damage, the damage is maximized."),
    Surge("The next time you cast a spell, do not roll on this chart."),
    Surge("The next time you cast a spell, roll twice on this chart. Both effects will apply."),
    Surge("For the {duration}, any spell you cast does not require a somatic component."),
    Surge("For the {duration}, any spell you cast does not require a verbal component."),
    # Actions
    Surge("You may immediately take 1 additional action."),
    Surge(
        "You stand at the center a circular wall of {element} with a radius of 15 feet. Any creature in any of the spaces covered by this wall must make a Dexterity saving throw against your spell DC or take 5d8 {element} damage. The wall remains for {duration_minutes}."
    ),
    # Movement and teleportation
    Surge("You teleport to an alternate plane, then return to the location where you started after 1 minute."),
    Surge("You teleport up to 60 feet to an unoccupied space that you can see."),
    Surge("Your speed {change_direction} by 10 feet for {duration}."),
    # Misc
    Surge("You're feeling lucky. Any time you make an ability check, roll 1d{dice_type} and add the result. This lasts {duration}."),
    PermStatChangeSurge("Your {stat} {change_direction} by {amount} permanently"),
    TempStatChangeSurge("Your {stat} {change_direction} by {amount} for {duration}."),
]


def random_surges(seed: int, count: int = 5) -> List[Tuple[str, str]]:
    if count < 5:
        count = 20
    if count > 100:
        count = 100

    rng = numpy.random.default_rng(seed)
    surges: Set[Surge] = set()
    attempts = 0
    while attempts < count * 2 and len(surges) < count:
        attempts += 1
        surges.add(rng.choice(SURGES))

    return [(surge.render(seed).capitalize(), repr(surge)) for surge in sorted(surges, key=lambda x: hash(x))]


def find_surge(seed: int, surge_id: str, raw: bool = False) -> Optional[Tuple[str, str]]:
    for surge in SURGES:
        if repr(surge) == surge_id:
            if raw:
                return surge._message, repr(surge)
            return surge.render(seed).capitalize(), repr(surge)
    return None
