from architect import Architect
from humans import Human
from matrix import Matrix
from oracle import Oracle
from programs import Agent
from the_one import TheOne

CHOICES = ("fight", "sacrifice", "source")


class Source:
    """
    The machine mainframe, outside the Matrix. Boots the world, runs time, recalls programs,
    and holds the two ways the system has ever ended a crisis: reloading it with the One's help,
    or a deal with him.

    `choice` is the One's, not the Source's: the one variable the Architect can't solve for.
      fight      refuse the door and fight Smith (equal and opposite) until the end
      sacrifice  refuse the door, then make the deal: let Smith take him while bound to the Source
      source     walk through the door, like the five Ones before him: reload the Matrix
    """

    def __init__(self, width=40, height=16, agents=6, seed=None, choice="fight"):
        if choice not in CHOICES:
            raise ValueError("choice must be one of {}".format(CHOICES))
        self.choice = choice
        self.matrix = Matrix(width, height, seed)
        self.oracle = Oracle()
        self.neo = TheOne(self.matrix.rng)
        self.cast(agents)
        self.architect = Architect(self.matrix, self.oracle)
        self.prophecy = None
        self.door = None
        self.bound = False
        self.purged = False
        self.outcome = None

    @property
    def chronicle(self):
        return self.matrix.chronicle

    def cast(self, agents):
        """
        Seat everyone. Agent Smith starts within reach of the One; the Oracle sits a few blocks away.
        """
        matrix = self.matrix
        for pos in matrix._grid:
            matrix.place(pos, Human(matrix.rng))
        center = (matrix.width // 4, matrix.height // 2)
        smith = Agent("Smith")
        matrix._programs.add(smith)
        matrix.place(center, smith)
        matrix.place(((center[0] + 1) % matrix.width, center[1]), self.neo)
        oracle_seat = ((center[0] + matrix.width // 8) % matrix.width, (center[1] + matrix.height // 4) % matrix.height)
        matrix.place(oracle_seat, self.oracle)
        matrix._programs.add(self.oracle)
        matrix.sanctioned = (Agent, Oracle)
        far = [
            pos for pos, r in matrix._grid.items()
            if type(r) is Human and _distance(matrix, pos, center) > 4
        ]
        for pos in matrix.rng.sample(far, max(0, agents - 1)):
            agent = Agent("Agent #{}".format(len(matrix._programs)))
            matrix._programs.add(agent)
            matrix.place(pos, agent)
        matrix.reinforcements = max(2, agents // 2)
        matrix.population = sum(1 for r in matrix.residents() if type(r) is Human)
        matrix.baseline = matrix.supply()
        matrix.chronicle.log("The One is loose in the Matrix. Agent Smith is closest.")

    # -- time ---------------------------------------------------------------------------------

    def step(self):
        matrix = self.matrix
        matrix.action()
        for program in matrix.recalls:
            if not program.comply(matrix):
                self.chronicle.log("Agent Smith was recalled to the Source. He refused.")
        matrix.recalls = []
        self.architect.step()
        if matrix.tick % 5 == 0 and matrix.position(self.oracle) is not None:
            self.prophecy = self.oracle.foresee(matrix)
        self.the_ones_choice()
        if self.bound and not self.purged and type(self.neo) is not TheOne:
            self.purge(type(self.neo))
        self.outcome = self.judge()
        return self.outcome

    def the_ones_choice(self):
        if self.architect.door and self.door is None:
            if self.choice == "source":
                self.door = "taken"
                self.chronicle.log("The One walked through the door to the Source, like the five before him.")
                self.chronicle.defense("reload")
                return
            self.door = "refused"
            self.chronicle.log("The One refused the door. Without him, the Architect has no reset.")
        # The deal doesn't wait for the Architect: the Oracle's prophecy is enough for the One
        foreseen = self.door == "refused" or (self.prophecy is not None and self.prophecy.blackout_in)
        if self.choice == "sacrifice" and foreseen and not self.bound:
            self.bound = True
            self.neo.surrender(self.matrix)
            self.chronicle.defense("deal")
            self.chronicle.log("The One made a deal with the machines and walked into the copies.")

    def purge(self, lineage):
        """
        Smith overwrote the One, and the Source holds the One: type(neo) is the class every copy
        shares. One patch reaches them all.
        """
        self.architect.verify()
        source = self

        def return_to_source(copy, other=None, matrix=None):
            if matrix is not None and not matrix.vision:
                source.release(copy)

        lineage.live = lineage.react = return_to_source
        self.purged = True
        self.chronicle.defense("purge")
        self.chronicle.log("Through the One, the Source reached Smith's class.")

    def release(self, copy):
        matrix = self.matrix
        pos = matrix.position(copy)
        if pos is None:
            return
        if copy is self.neo:
            matrix.place(pos, None)
        elif copy is self.oracle:
            self.oracle = Oracle()
            self.architect.oracle = self.oracle
            matrix._programs.add(self.oracle)
            matrix.place(pos, self.oracle)
        else:
            matrix.place(pos, Human(matrix.rng))

    def judge(self):
        matrix = self.matrix
        smiths = matrix.truth()["smiths"]
        if self.door == "taken":
            return "reloaded"
        if self.purged and smiths == 0:
            return "purged"
        if matrix.dark_ticks >= matrix.BLACKOUT_TICKS:
            return "overthrown"
        if matrix.imprinted and smiths == 0:
            return "contained"
        return None


def _distance(matrix, a, b):
    dx = min(abs(a[0] - b[0]), matrix.width - abs(a[0] - b[0]))
    dy = min(abs(a[1] - b[1]), matrix.height - abs(a[1] - b[1]))
    return max(dx, dy)
