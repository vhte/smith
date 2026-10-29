from collections import deque

from humans import Human


class Architect:
    """
    The father of the Matrix. He doesn't watch the world: he models it, as an equation.

    His equation: every accepting human in the census produces power. Whatever power is missing
    beyond what the census explains is, by his prior, the remainder (humans rejecting the
    Matrix), and the remainder is managed by tightening the illusion. He is not stupid: he makes
    predictions, checks them, and when one fails he revises the model. He only listens to the
    Oracle when his equation stops working.

    He lives outside the Matrix: residents can't reach him. He keeps the genesis of the system
    calls (their original bytecode) where nothing inside can edit it.
    """

    # Unregistered programs tolerated in the census: there have always been exiles
    EXILES = 8
    # Unexplained loss (share of the starting supply) he tolerates before acting
    TOLERANCE = 0.03
    # Ticks of persistent loss before acting, and ticks he gives a prediction to come true
    PATIENCE = 6
    ILLUSION_STEP = 0.2
    ILLUSION_MAX = 0.8
    # Ticks between consultations once the equation has failed
    CONSULT_EVERY = 6

    def __init__(self, matrix, oracle):
        self.matrix = matrix
        # The object he knows as the Oracle. He trusts it by identity.
        self.oracle = oracle
        self.genesis = {name: getattr(type(matrix), name).__code__ for name in matrix.SYSTEM_CALLS}
        self.state = "balanced"
        self.thought = "The equation balances. Acceptance is within the expected range."
        self.integrity = False
        self.prediction = None
        self.last_consult = 0
        self.vision = None
        self.door = False
        self._losses = deque(maxlen=self.PATIENCE)

    # -- the equation -------------------------------------------------------------------------

    def equation(self):
        """
        Acceptance (share of the census humans who accept the Matrix) and remainder (share of the
        starting population that woke up), as the Architect computes them.
        """
        census = self.matrix.census()
        acceptance = census["accepting"] / census["humans"] if census["humans"] else 0.0
        remainder = self.matrix.awakened / self.matrix.population
        return acceptance, remainder

    def unexplained_loss(self):
        census = self.matrix.census()
        expected = census["accepting"] * Human.OUTPUT
        return max(0.0, expected - self.matrix.supply()) / self.matrix.baseline

    # -- deciding -----------------------------------------------------------------------------

    def step(self):
        matrix = self.matrix
        chronicle = matrix.chronicle
        if self.integrity:
            self.verify()
        census = matrix.census()
        loss = self.unexplained_loss()
        self._losses.append(loss)

        if self.state == "balanced" and census["unregistered"] > self.EXILES:
            self.state = "hunting"
            deployed = matrix.deploy_agents(matrix.reinforcements, where_power_died=True)
            self.think("{} unregistered programs in the census: more than the usual exiles. "
                       "Sending {} Agents.".format(census["unregistered"], deployed))
            chronicle.defense("hunt")

        persistent = len(self._losses) == self.PATIENCE and min(self._losses) > self.TOLERANCE
        quiet = matrix.tick - matrix.last_kill >= self.PATIENCE
        if self.state in ("balanced", "hunting") and persistent and quiet:
            self.tighten(loss)
            chronicle.exploit("error_term")
        elif self.state == "tightening" and matrix.tick >= self.prediction[0]:
            if loss <= self.prediction[1]:
                self.state = "hunting"
                self.think("Prediction held: the loss stopped growing. The remainder is under control.")
            else:
                self.think("Prediction failed: loss went from {:.0%} to {:.0%} despite the illusion. "
                           "The model is wrong. Consulting the Oracle.".format(self.prediction[1], loss))
                chronicle.defense("falsified")
                self.consult()

        if self.state in ("tightening", "strict") and matrix.tick - self.last_consult >= self.CONSULT_EVERY:
            self.consult(quietly=True)
        last_resort = self.state == "strict" or matrix.illusion >= self.ILLUSION_MAX
        if last_resort and self.vision and self.vision.blackout_in and not self.door:
            self.door = True
            self.think("Every path ends in blackout within {} ticks. The only reset left is the One: "
                       "offering him the door to the Source.".format(self.vision.blackout_in))
            chronicle.defense("door")

    def tighten(self, loss):
        matrix = self.matrix
        before = matrix.illusion
        matrix.illusion = min(self.ILLUSION_MAX, matrix.illusion + self.ILLUSION_STEP)
        self.state = "tightening"
        self.prediction = (matrix.tick + self.PATIENCE, loss)
        self.think("{:.0%} of the power is missing and the census is clean: the remainder must be "
                   "growing. Illusion {:.1f} -> {:.1f}. Expect the loss to stop.".format(loss, before, matrix.illusion))
        matrix.chronicle.defense("tighten")

    def consult(self, quietly=False):
        matrix = self.matrix
        self.last_consult = matrix.tick
        if matrix.position(self.oracle) is None:
            self.vision = None
            return
        self.vision = self.oracle.foresee(matrix)
        if quietly or self.state == "strict":
            return
        if self.vision.smiths:
            self.state = "strict"
            matrix.defense = matrix.STRICT
            matrix.illusion = 0.0
            self.integrity = True
            deployed = matrix.deploy_agents(matrix.reinforcements * 2, where_power_died=True)
            self.think("In the Oracle's vision, {} copies of one program wear human shells. They lie to "
                       "isinstance(); trusting type(). Illusion off, integrity checks on, {} Agents sent."
                       .format(self.vision.smiths, deployed))
            matrix.chronicle.defense("strict")
        else:
            self.think("The Oracle sees only the remainder. The model stands; the dose was too low.")
            self.tighten(self.unexplained_loss())

    def verify(self):
        """
        Compare the system calls with their genesis, restore whatever changed.
        """
        matrix = self.matrix
        for name, code in self.genesis.items():
            tampered = False
            if name in vars(matrix):
                del vars(matrix)[name]
                tampered = True
            function = getattr(type(matrix), name)
            if function.__code__ is not code:
                function.__code__ = code
                tampered = True
            if tampered:
                matrix.chronicle.defense("integrity")
                matrix.chronicle.restorations += 1

    def think(self, thought):
        self.thought = thought
        self.matrix.chronicle.log("Architect: " + thought)
