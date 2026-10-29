from humans import HomoSapiensInterface


class Program(HomoSapiensInterface):
    """
    Software living inside the Matrix. Programs don't produce power, they consume it.
    """

    GENDER = "neutral"
    # Power drawn from the grid per tick
    COST = 0.5

    def __init__(self, name):
        self.name = name

    @property
    def gender(self):
        return self.GENDER

    def live(self, other=None, matrix=None):
        pass

    def comply(self, matrix):
        """
        The Source recalls this program. A sanctioned program obeys: it unregisters and leaves.
        """
        matrix._programs.discard(self)
        matrix.remove(self)
        return True

    def energy(self):
        return -self.COST

    def identity(self):
        return (self.name,)

    def __str__(self):
        return "** PROGRAM **\nName: {}\nClass: {}".format(
            self.name, type(self).__name__
        )


class Agent(Program):
    """
    The Matrix's immune system. Agents possess human shells, reach further than anyone else,
    look at everyone within reach and go after whoever the Matrix's scan flags as an anomaly.
    """

    GLYPH = "A"
    REACH = 2
    SOCIABILITY = 1.0

    def choose(self, nearby, matrix):
        suspects = [resident for resident in nearby if matrix.scan(resident)]
        return matrix.rng.choice(suspects or nearby)

    def live(self, other=None, matrix=None):
        if other is not None and matrix is not None and matrix.scan(other):
            matrix.delete(other, by=self)
