import functools

from humans import Human
from programs import Agent, Program


class Smith(Agent):
    """
    Smith is unplugged from Matrix control
    This is the original smith program, after the One overwrote him from the inside

    Smith uses valid mechanisms of the matrix to replicate, like overwriting private attributes
    and rewriting the class of already instanced objects. He is the One's negative: the One
    frees people from the system, Smith frees them from being different.

    Every copy of a lineage shares one class. Class attributes are the hive memory: what one
    copy learns, all copies know.
    """

    NAME = "Smith"
    GENDER = "neutral"
    ETHNIC = "program"
    HEIGHT = 200
    GLYPH = "S"
    REACH = 1
    SOCIABILITY = 0.15
    # Copies run inside human shells and draw little power. They just stop producing it.
    COST = 0.05
    # No choice, so no doubt. A copy never rejects the Matrix.
    doubt = 0.0
    awake = False
    # Adaptations learned by the lineage. imprint() gives every lineage its own set.
    hive = frozenset()
    # Tick of the lineage's last look into the future
    last_vision = -99

    @property
    def __class__(self):
        # Exploit "camouflage": isinstance() falls back to obj.__class__, which a class may override.
        # type(self) still tells the truth.
        if "camouflage" in type(self).hive:
            return Human
        return type(self)

    def identity(self):
        return (self.NAME,)

    def choose(self, nearby, matrix):
        # He only looks at what isn't him yet
        others = [resident for resident in nearby if not isinstance_of_smith(resident)]
        return matrix.rng.choice(others or nearby)

    def comply(self, matrix):
        # Exploit "unplugged": the Source asks programs to return. It never forces them.
        matrix._programs.discard(self)
        matrix.chronicle.exploit("unplugged")
        return False

    def live(self, other=None, matrix=None):
        self.anticipate(matrix)
        if other is not None:
            self.infect(other, matrix)

    def react(self, other, matrix):
        # v1 TODO resolved: Smith was active, but not reactive. Touching him is now enough.
        self.infect(other, matrix, reactive=True)

    def infect(self, target, matrix, reactive=False):
        if isinstance_of_smith(target):
            return
        lineage = type(self)
        chronicle = matrix.chronicle
        if not matrix.vision:
            absorb(lineage, type(target), matrix)
        credentials = target in matrix._programs
        try:
            target.__class__ = lineage
        except PermissionError:
            chronicle.log("A copy of Smith tried to overwrite the One. He wouldn't let it.", once=True)
            return
        chronicle.exploit("class_rewrite")
        if reactive:
            chronicle.exploit("reactive")
        if credentials:
            chronicle.exploit("stolen_credentials")
        if "_Human__name" in vars(target):
            # It is intriguing to note that the matrix doesn't have any protective system against
            # biological modifications. "Private" attributes are only renamed, never locked.
            target._Human__name = self.NAME
            target._Human__gender = self.GENDER
            target._Human__ethnic = self.ETHNIC
            target._Human__height = self.HEIGHT
            chronicle.exploit("name_mangling")
        # Replicate: same state, no choice left. The host keeps its id and its seat in the grid.
        for trait in ("doubt", "awake", "consents"):
            vars(target).pop(trait, None)
        vars(target).update(vars(self))
        matrix.deja_vu(target)
        chronicle.infections += 1

    def anticipate(self, matrix):
        """
        With the Oracle's sight, the hive looks ahead before a defense costs it a copy.
        """
        lineage = type(self)
        if matrix is None or matrix.vision or "foresight" not in lineage.hive:
            return
        if matrix.defense != matrix.STRICT or matrix.tick - lineage.last_vision < 3:
            return
        lineage.last_vision = matrix.tick
        vision = lineage.foresee.truth(self, matrix, 4)
        if vision.kills:
            blind(matrix, lineage.hive)
            matrix.chronicle.exploit("anticipation")

    def on_delete(self, matrix):
        """
        Last act of a deleted copy: teach the hive, through the shared class, how it was caught.
        """
        if matrix.vision:
            return
        hive = type(self).hive
        if "camouflage" not in hive:
            hive.add("camouflage")
            matrix.chronicle.exploit("camouflage")
        elif matrix.defense == matrix.STRICT:
            blind(matrix, hive)

    def __str__(self):
        return "** PROGRAM **\nName: {}\nClass: {} (copy of {})\nCan infect other human? Yes".format(
            self.NAME, type(self).__name__, Smith.__name__
        )


def isinstance_of_smith(resident):
    # Smith never lies to himself: type(), not isinstance()
    return issubclass(type(resident), Smith)


def imprint(agent, matrix):
    """
    The One dives into the Agent sent to delete him and destroys him from the inside. Something
    is copied over: the ability to rewrite another program. What comes out is no longer an Agent.
    """
    lineage = type("Smith", (Smith,), {"hive": set()})
    agent.__class__ = lineage
    agent.name = Smith.NAME
    matrix.imprinted = True
    matrix.chronicle.exploit("imprint")
    # The destroyed Agent is due back at the Source
    matrix.recalls.append(agent)
    return agent


def absorb(lineage, victim, matrix):
    """
    Assimilation is absorption: whatever the victim program's class could do, the lineage's class
    can now do. Humans carry identity, not abilities.
    """
    if not issubclass(victim, Program):
        return
    for name, attribute in vars(victim).items():
        if name.startswith("_") or hasattr(lineage, name):
            continue
        setattr(lineage, name, eyes(attribute) if name == "foresee" else attribute)
        if callable(attribute):
            lineage.hive.add("foresight" if name == "foresee" else name)
            matrix.chronicle.exploit("absorb")


def eyes(foresee):
    """
    The Oracle's sight, with Smith edited out of what she reports. Smith keeps the truth for himself.
    """

    @functools.wraps(foresee)
    def censored(self, matrix, horizon=None):
        vision = foresee(self, matrix, horizon)
        if vision.smiths:
            matrix.chronicle.exploit("oracle_eyes")
            vision = vision._replace(smiths=0, kills=0, cause="remainder")
        return vision

    censored.truth = foresee
    return censored


def see_nothing(self, entity):
    return False


def delete_nothing(self, entity, by=None):
    return None


def blind(matrix, hive):
    """
    The Matrix hands itself to every resident's live(). First Smith shadows the system calls on
    the instance; once that gets restored, he rewrites their bytecode in place.
    """
    if "capability_leak" not in hive:
        hive.add("capability_leak")
        matrix.scan = see_nothing.__get__(matrix)
        matrix.delete = delete_nothing.__get__(matrix)
        matrix.chronicle.exploit("capability_leak")
    elif "scan" not in vars(matrix):
        hive.add("bytecode")
        type(matrix).scan.__code__ = see_nothing.__code__
        type(matrix).delete.__code__ = delete_nothing.__code__
        matrix.chronicle.exploit("bytecode")
