import copy
import math
import random
import types
from collections import Counter

from chronicle import Chronicle
from humans import Human
from programs import Agent, Program


def _compile(function):
    """
    A private copy of a function: same code, new function object.
    """
    clone = types.FunctionType(
        function.__code__, function.__globals__, function.__name__, function.__defaults__, function.__closure__
    )
    clone.__kwdefaults__ = function.__kwdefaults__
    clone.__qualname__ = function.__qualname__
    clone.__doc__ = function.__doc__
    return clone


class Matrix:
    """
    The simulated world: a toroidal grid of seats, a tick loop, an interaction protocol and two
    system calls (scan, delete).

    The Matrix doesn't know about the Source, the Architect or the One's choices: those live
    outside it (source.py). What lives inside receives a reference to the Matrix on every turn,
    and that reference is all a resident can ever reach.
    """

    SYSTEM_CALLS = ("scan", "delete")
    POLITE, STRICT = "isinstance() scan", "type() scan"
    # Share of the starting supply the machines need just to keep running
    DEMAND = 0.6
    # Power burned per point of illusion, as a share of the starting supply
    ILLUSION_COST = 0.25
    BLACKOUT_TICKS = 3

    def __new__(cls, *args, **kwargs):
        # Every Matrix boots its own compiled copy of the system calls, so whatever happens to
        # them stays in this run (and a forked vision gets its own copy too).
        compiled = type(cls.__name__, (cls,), {name: _compile(getattr(cls, name)) for name in cls.SYSTEM_CALLS})
        return super().__new__(compiled)

    def __init__(self, width=40, height=16, seed=None):
        self.seed = seed if seed is not None else random.randrange(10_000)
        self.rng = random.Random(self.seed)
        self.width, self.height = width, height
        self.tick = 0
        self.chronicle = Chronicle()
        self.defense = self.POLITE
        self.sanctioned = (Agent,)
        self.illusion = 0.0
        self.awakened = 0
        self.smith_deletions = 0
        self.last_kill = 0
        self.dark_ticks = 0
        self.imprinted = False
        self.vision = False
        self.recalls = []
        self._programs = set()
        self._grid = {(x, y): None for y in range(self.height) for x in range(self.width)}
        self._seats = {}
        self.baseline = 1.0

    # -- seats --------------------------------------------------------------------------------

    def place(self, pos, entity):
        previous = self._grid.get(pos)
        if previous is not None:
            self._seats.pop(id(previous), None)
        self._grid[pos] = entity
        if entity is not None:
            self._seats[id(entity)] = pos

    def swap(self, a, b):
        first, second = self._grid[a], self._grid[b]
        self.place(a, None)
        self.place(b, None)
        self.place(a, second)
        self.place(b, first)

    def remove(self, entity):
        pos = self.position(entity)
        if pos is not None:
            self.place(pos, None)
        return pos

    def position(self, entity):
        return self._seats.get(id(entity))

    def at(self, pos):
        return self._grid.get(pos)

    def residents(self):
        return [r for r in self._grid.values() if r is not None]

    def cells(self, pos, reach):
        x, y = pos
        return [
            ((x + dx) % self.width, (y + dy) % self.height)
            for dx in range(-reach, reach + 1)
            for dy in range(-reach, reach + 1)
            if (dx, dy) != (0, 0)
        ]

    def neighbors(self, pos, reach):
        return [self._grid[c] for c in self.cells(pos, reach) if self._grid[c] is not None]

    def deploy_agents(self, count, where_power_died=False):
        """
        Agents possess human shells. When asked, they possess shells next to residents that
        stopped producing power: the census can be fooled, the power meter can't.
        """
        shells = [pos for pos, r in self._grid.items() if type(r) is Human]
        if where_power_died:
            hot = [pos for pos in shells if any(self._dark(n) for n in self.neighbors(pos, 1))]
            shells = hot or shells
        deployed = 0
        for pos in self.rng.sample(shells, min(count, len(shells))):
            agent = Agent("Agent #{}".format(len(self._programs) + 1))
            self._programs.add(agent)
            self.place(pos, agent)
            deployed += 1
        return deployed

    def _dark(self, resident):
        return resident.energy() <= 0 and resident not in self._programs and not resident.awake

    # -- time ---------------------------------------------------------------------------------

    def action(self):
        """
        This represents time. Everybody gets a turn, in random order
        """
        self.tick += 1
        self.chronicle.tick = self.tick
        seats = [pos for pos, r in self._grid.items() if r is not None]
        self.rng.shuffle(seats)
        for pos in seats:
            actor = self._grid[pos]
            if actor is None:
                continue
            other = None
            if self.rng.random() < actor.SOCIABILITY:
                nearby = self.neighbors(pos, actor.REACH)
                other = actor.choose(nearby, self) if nearby else None
            self.interact(actor, other)
        self.dark_ticks = self.dark_ticks + 1 if self.supply() < self.demand() else 0

    def interact(self, actor, other):
        actor.live(other, self)
        if other is not None and self.position(actor) is not None and self.position(other) is not None:
            other.react(actor, self)

    def awaken(self, human):
        """
        A human rejected the Matrix. Their pod empties: one more for the remainder.
        """
        self.remove(human)
        self.awakened += 1

    def deja_vu(self, entity):
        """
        Something changed in the code. Whoever is close notices.
        """
        pos = self.position(entity)
        if pos is None:
            return
        for neighbor in self.neighbors(pos, 1):
            if hasattr(neighbor, "feel_deja_vu"):
                neighbor.feel_deja_vu()

    def fork(self):
        """
        A full copy of the world that runs ahead without touching this one.
        """
        vision = copy.deepcopy(self)
        vision._seats = {id(r): pos for pos, r in vision._grid.items() if r is not None}
        vision.rng = random.Random(self.rng.random())
        vision.vision = True
        vision.recalls = []
        return vision

    # -- system calls -------------------------------------------------------------------------

    def scan(self, entity):
        """
        Is this entity an anomaly? How hard the Matrix looks depends on the defense level.
        """
        if self.defense == self.POLITE:
            if isinstance(entity, Human):
                return entity.awake
            return not (isinstance(entity, Program) and entity in self._programs)
        if type(entity) is Human:
            return entity.awake
        return not (type(entity) in self.sanctioned and entity in self._programs)

    def delete(self, entity, by=None):
        pos = self.position(entity)
        if pos is None or entity.resist(by, self):
            return
        self.deja_vu(entity)
        self.place(pos, None)
        self._programs.discard(entity)
        if hasattr(entity, "on_delete"):
            self.smith_deletions += 1
            self.last_kill = self.tick
            entity.on_delete(self)

    # -- measurements -------------------------------------------------------------------------

    def supply(self):
        return sum(max(r.energy(), 0.0) for r in self.residents())

    def demand(self):
        draw = sum(-min(r.energy(), 0.0) for r in self.residents())
        return self.baseline * (self.DEMAND + self.illusion * self.ILLUSION_COST) + draw

    def truth(self):
        """
        Who is who, according to type(): what an outside observer sees.
        """
        counts = Counter(humans=0, agents=0, smiths=0, oracle=0, the_one=0, empty=0)
        for resident in self._grid.values():
            if resident is None:
                counts["empty"] += 1
            elif hasattr(type(resident), "hive"):
                counts["smiths"] += 1
            elif type(resident) is Human:
                counts["humans"] += 1
            elif type(resident) is Agent:
                counts["agents"] += 1
            elif resident.awake:
                counts["the_one"] += 1
            else:
                counts["oracle"] += 1
        return counts

    def census(self):
        """
        Who is who, according to isinstance(): what the Matrix believes.
        """
        counts = Counter(humans=0, accepting=0, programs=0, unregistered=0, awake=0)
        for resident in self.residents():
            if isinstance(resident, Human):
                counts["humans"] += 1
                counts["awake" if resident.awake else "accepting"] += 1
            elif isinstance(resident, Program):
                counts["programs"] += 1
                if resident not in self._programs:
                    counts["unregistered"] += 1
        return counts

    def entropy(self):
        """
        Shannon entropy of identities, in bits: how many different people there still are.
        """
        identities = Counter(r.identity() for r in self.residents())
        total = sum(identities.values())
        return -sum(n / total * math.log2(n / total) for n in identities.values()) if total else 0.0

    def get_grid(self):
        return [[self._grid[(x, y)] for x in range(self.width)] for y in range(self.height)]
