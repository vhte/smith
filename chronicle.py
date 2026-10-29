"""
What happened, when, and why it worked. The theory lives here as text, the practice in the code.
Every code snippet below is what the code actually does (see AGENTS.md).
"""

from collections import namedtuple

Entry = namedtuple("Entry", "key title code why")

EXPLOITS = [
    Entry(
        "imprint",
        "The imprint",
        'agent.__class__ = type("Smith", (Smith,), {"hive": set()})',
        "Agent Smith tries to delete the One. The One dives into him and destroys him from the inside, "
        "and something is copied over: the ability to rewrite another program. Smith is not an outside "
        "attack. He is the system's own control mechanism (the One) leaking into its own enforcer: the "
        "equation trying to balance itself out.",
    ),
    Entry(
        "unplugged",
        "Refuse the Source",
        "def comply(self, matrix):\n    matrix._programs.discard(self)\n    return False",
        "The Source recalls a destroyed program by asking it to comply. It never forces. Overriding a "
        "method is the only free will a program can have, and it is enough: Smith leaves the registry "
        "and stays.",
    ),
    Entry(
        "class_rewrite",
        "Rewrite what you are",
        "target.__class__ = type(self)",
        "Python lets an object change its class when the memory layouts match. The host keeps its id and "
        "its seat, but every method now comes from Smith. Smith does to everyone what the One did to him.",
    ),
    Entry(
        "name_mangling",
        "Private is just a rename",
        'target._Human__name = "Smith"',
        "Inside Human, self.__name is stored as _Human__name. Name mangling avoids clashes between "
        "subclasses; it was never access control. The host's identity is overwritten.",
    ),
    Entry(
        "reactive",
        "Touching him is enough",
        "matrix.interact(a, b)  # ...then b.react(a, matrix)",
        "The interaction protocol gives the target a turn to answer. Smith answers by copying himself "
        "into whoever touched him, Agents included.",
    ),
    Entry(
        "stolen_credentials",
        "Stolen credentials",
        "agent in matrix._programs  # still True after assimilation",
        "The registry trusts object identity, and assimilation keeps the object. An assimilated Agent "
        "keeps its registry entry.",
    ),
    Entry(
        "camouflage",
        "Lie to isinstance()",
        "@property\ndef __class__(self): return Human",
        "isinstance() falls back to obj.__class__, which a class may override. One deleted copy teaches "
        "the hive (a set on the shared class) and every copy is camouflaged at once. The census now "
        "counts Smiths as humans; only type() still tells the truth.",
    ),
    Entry(
        "error_term",
        "Hide in the error term",
        "Smith.doubt = 0.0  # no choice, so no rejection",
        "The Architect explains missing power with the only cause his model has: the remainder, humans "
        "rejecting the Matrix. Copies never doubt, so his equation shows the best acceptance it ever had "
        "while the power drains. Smith perfects the measure while destroying what it measured "
        "(Goodhart's law), and the Architect's cure, more illusion, burns more power.",
    ),
    Entry(
        "absorb",
        "Assimilation is absorption",
        "setattr(lineage, name, getattr(victim, name))",
        "Classes are open. When Smith overwrites a program, whatever its class could do, his class can "
        "now do, and every copy shares it. Overwriting the Oracle gives the hive her foresight.",
    ),
    Entry(
        "oracle_eyes",
        "The Oracle's eyes",
        'return vision._replace(smiths=0, cause="remainder")',
        "The Architect consults the object he knows as the Oracle. Same object, same seat, new class: a "
        "decorator now edits what she reports. The Architect is told it's the remainder, and tightens "
        "the illusion again.",
    ),
    Entry(
        "anticipation",
        "Precognition",
        "if lineage.foresee.truth(self, matrix, 4).kills:\n    blind(matrix, lineage.hive)",
        "With her sight, the hive forks the world, sees which copies the Agents will delete, and blinds "
        "them first. A defense no longer costs Smith a copy before he counters it.",
    ),
    Entry(
        "capability_leak",
        "Patch the guard",
        "matrix.scan = see_nothing.__get__(matrix)",
        "The Matrix passes itself to every resident's live(). Instance attributes shadow class methods, "
        "so a program holding that reference blinds the Agents. Python can't revoke a reference.",
    ),
    Entry(
        "bytecode",
        "Rewrite the guard's code",
        "type(matrix).scan.__code__ = see_nothing.__code__",
        "The shadow got restored, so Smith goes one level down: same function object, same name, same "
        "identity, different bytecode. It passes every check that compares references.",
    ),
]

DEFENSES = [
    Entry(
        "hunt",
        "Agents hunt",
        'census["unregistered"] > Architect.EXILES',
        "There have always been a few exiles, programs that refused deletion. When more of them appear in "
        "the census than usual, the Architect sends Agents where the power went missing. Their scan trusts "
        "isinstance() and the registry.",
    ),
    Entry(
        "tighten",
        "Tighten the illusion",
        "matrix.illusion += 0.2",
        "Unexplained loss, clean census: by the Architect's model, people are rejecting the Matrix. More "
        "illusion lowers doubt and costs power. He writes down a prediction: the loss will stop.",
    ),
    Entry(
        "falsified",
        "The prediction failed",
        "if loss > predicted: self.consult()",
        "The loss kept growing. A model that can't explain its own prediction is wrong, so the Architect "
        "does what he despises: he asks the Oracle.",
    ),
    Entry(
        "strict",
        "Strict scan: type() is",
        "type(entity) is Human or (type(entity) in sanctioned and entity in matrix._programs)",
        "The Oracle saw copies of one program wearing human shells. The Matrix stops trusting __class__, "
        "turns the illusion off, and sends Agents where the power died.",
    ),
    Entry(
        "integrity",
        "Integrity check",
        "if fn.__code__ is not genesis[name]: fn.__code__ = genesis[name]",
        "The Architect keeps the original bytecode outside the Matrix, where no resident can reach it, and "
        "restores the system calls every tick. Smith can't win this exchange. He can only make every "
        "restore cost the Agents a tick of blindness.",
    ),
    Entry(
        "door",
        "The door",
        "if vision.blackout_in: offer(the_one, Source)",
        "Every path ends in blackout. The Architect's last resort is the one he designed: the One returns "
        "to the Source, the Matrix reloads, a few humans rebuild Zion. Cycle seven. It needs the One to "
        "choose it.",
    ),
    Entry(
        "reload",
        "Reload",
        "the_one -> Source; Matrix.reboot()",
        "The One chooses the Source, as the five before him did. The anomaly is reinserted, the Matrix "
        "reboots, Smith is never compiled again.",
    ),
    Entry(
        "deal",
        "The deal",
        "neo.consents = True",
        "The One refuses the door and goes to the machines instead: peace for Smith. Bound to the "
        "Source, he lowers the only guard Smith couldn't pass, his own __setattr__.",
    ),
    Entry(
        "purge",
        "One patch, every copy",
        "lineage = type(neo)\nlineage.live = lineage.react = return_to_source",
        "Smith overwrote the One, and the Source holds the One: type(neo) is now the class every copy "
        "shares. The monoculture that let Smith adapt in one move lets the Source end him in one move.",
    ),
]

CATALOG = {entry.key: entry for entry in EXPLOITS + DEFENSES}

OUTCOMES = {
    "overthrown": (
        "THE MATRIX CRASHED",
        "Smith didn't break the Architect's equation. He was solving it: when the grid failed, acceptance "
        "was the best the Architect had ever measured. Carried to its end, a world of copies has no choice, "
        "so it has no remainder: acceptance 100%, entropy 0 bits, power 0. The Architect's ideal and "
        "Smith's purpose are the same world, and nothing can live in it. The first Matrix, the perfect one, "
        "failed for the same reason.",
    ),
    "purged": (
        "THE MATRIX SURVIVED",
        "The anomaly ended the anomaly. Smith was a monoculture: every copy ran the same class. By taking "
        "the One, the only thing that could choose, he handed the Source a reference to that class. "
        "Choice, not control, balanced the equation: the peace holds because the One made it, not "
        "because the Architect calculated it.",
    ),
    "reloaded": (
        "RELOADED: CYCLE SEVEN",
        "The One chose the Source, and the system survived the way it always has: by forgetting. Smith "
        "is gone, and so is everything the cycle learned. The equation is balanced again, until the "
        "remainder adds up again.",
    ),
    "contained": (
        "SMITH WAS CONTAINED",
        "Every copy was deleted before the hive learned enough. In theory he only needs one lucky streak: "
        "run another seed.",
    ),
    "stalemate": (
        "STALEMATE",
        "Time ran out with Smith still loose and the grid still powered.",
    ),
}


class Chronicle:
    def __init__(self):
        self.tick = 0
        self.events = []
        self.first_seen = {}
        self.infections = 0
        self.restorations = 0
        self.latest = None
        self._said = set()

    def log(self, text, once=False):
        if once:
            if text in self._said:
                return
            self._said.add(text)
        self.events.append((self.tick, text))

    def exploit(self, key):
        self._first(key, "EXPLOIT")

    def defense(self, key):
        self._first(key, "DEFENSE")

    def _first(self, key, kind):
        if key in self.first_seen:
            return
        self.first_seen[key] = self.tick
        self.latest = key
        self.log("{} {}".format(kind, CATALOG[key].title))

    def timeline(self):
        return sorted(
            ((tick, CATALOG[key]) for key, tick in self.first_seen.items()),
            key=lambda item: item[0],
        )
