from humans import Human
from matrix import Matrix
from programs import Agent
from smith import imprint, isinstance_of_smith


class TheOne(Human):
    """
    Neo. The sum of the remainder of an unbalanced equation: choice, concentrated in one person.

    He is awake (he produces no power) and he sees the code: he picks Smith out of any crowd with
    type(), and he deletes through the Matrix's own class, past anything patched on the instance.
    Nobody can rewrite him unless he chooses it.
    """

    NAME = ["Thomas A. Anderson"]
    GENDER = ["male"]
    GLYPH = "N"
    REACH = 3
    SOCIABILITY = 1.0

    def __init__(self, rng=None):
        super().__init__(rng)
        self.doubt = 1.0
        self.awake = True
        self.consents = False

    def __setattr__(self, name, value):
        if name == "__class__" and not self.consents:
            raise PermissionError("the One can't be overwritten against his will")
        object.__setattr__(self, name, value)

    def live(self, other=None, matrix=None):
        if self.consents or other is None or not isinstance_of_smith(other):
            return
        # Matrix.delete, not matrix.delete: the code behind whatever Smith did to this world
        Matrix.delete(matrix, other, by=self)
        matrix.chronicle.log("The One deleted a copy of Smith.", once=True)

    def choose(self, nearby, matrix):
        copies = [resident for resident in nearby if isinstance_of_smith(resident)]
        return matrix.rng.choice(copies or nearby)

    def resist(self, attacker, matrix):
        if not matrix.imprinted and type(attacker) is Agent:
            imprint(attacker, matrix)
            matrix.chronicle.log("The One dove into Agent Smith and destroyed him from the inside.")
            self.fly(matrix)
        return True

    def fly(self, matrix, destination=None):
        """
        He moves anywhere, by default to the opposite side of the world. Whoever sat there takes
        his old seat.
        """
        x, y = matrix.position(self)
        destination = destination or ((x + matrix.width // 2) % matrix.width, (y + matrix.height // 2) % matrix.height)
        matrix.swap((x, y), destination)

    def surrender(self, matrix):
        """
        The deal: stop fighting, lower the guard, and land where the copies are thickest.
        """
        self.consents = True
        seats = [pos for pos, r in matrix._grid.items() if r is not None and not isinstance_of_smith(r)]
        crowd = max(seats, key=lambda pos: sum(isinstance_of_smith(n) for n in matrix.neighbors(pos, 1)))
        if matrix.at(crowd) is not self:
            self.fly(matrix, crowd)

    def energy(self):
        return 0.0

    def identity(self):
        return ("Neo",)
