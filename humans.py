import random


class HomoSapiensInterface:
    """
    The contract of everything that lives inside the Matrix.

    Humans implement it because they are human. Programs (Agents, the Oracle, Smith) implement
    it because the Matrix only renders people: a program has to wear a human shell.
    """

    GLYPH = "?"
    # Chance of meeting someone during a tick, instead of acting alone
    SOCIABILITY = 0.5
    # How far (in cells) this resident reaches when it meets someone
    REACH = 1
    # Doubt about the world. Reaching 1.0 means rejecting the Matrix (waking up)
    doubt = 0.0
    awake = False

    @property
    def gender(self):
        raise NotImplementedError(
            "This method should be implemented in children classes."
        )

    def live(self, other=None, matrix=None):
        """
        Act during a tick. `other` is who this resident met, if anyone.
        """
        raise NotImplementedError(
            "This method should be implemented in children classes."
        )

    def choose(self, nearby, matrix):
        """
        Pick who to meet among the residents within reach. Most residents don't choose.
        """
        return matrix.rng.choice(nearby)

    def react(self, other, matrix):
        """
        Answer to being acted upon by `other`. Doing nothing is a valid answer.
        """

    def resist(self, attacker, matrix):
        """
        Answer to a deletion. True means the deletion didn't happen.
        """
        return False

    def energy(self):
        """
        Power this resident adds to (positive) or draws from (negative) the grid.
        """
        return 0.0

    def identity(self):
        """
        What makes this resident distinguishable from the others.
        """
        return (type(self).__name__,)


class Human(HomoSapiensInterface):
    """
    A bluepill. Lives, meets people, doubts, and produces the bioelectric power the machines run on.

    Doubt is where choice lives: it drifts at random every tick. The Oracle's design keeps most
    people accepting the Matrix; the few whose doubt reaches 1.0 wake up and leave. That remainder
    is the price of choice.
    """

    NAME = ["John Doe", "Jane Doe"]
    GENDER = ["male", "female"]
    ETHNIC = ["white", "black", "yellow", "multiracial"]
    HEIGHT = [130, 200]
    GLYPH = "o"
    SOCIABILITY = 0.1
    # Bioelectric power produced per tick
    OUTPUT = 1.0
    # Random drift of doubt per tick: choice
    CHOICE = 0.04
    # Doubt added when the world glitches nearby
    DEJA_VU = 0.15
    # How much each point of illusion pulls doubt down per tick
    COMFORT = 0.03

    def __init__(self, rng=None):
        rng = rng or random
        name = rng.randint(0, len(self.NAME) - 1)
        # Strictly private, can't be changed (or so the Matrix believes, see smith.py)
        self.__name = self.NAME[name]
        self.__gender = self.GENDER[name]
        self.__ethnic = self.ETHNIC[rng.randint(0, len(self.ETHNIC) - 1)]
        self.__height = rng.randint(self.HEIGHT[0], self.HEIGHT[1])
        self.doubt = rng.random() * 0.3

    def live(self, other=None, matrix=None):
        """
        Usual human activity. Can interact with other humans or not. Either way, they wonder.
        """
        if matrix is None:
            return
        drift = matrix.rng.gauss(0.0, self.CHOICE) - matrix.illusion * self.COMFORT
        self.doubt = max(0.0, self.doubt + drift)
        if self.doubt >= 1.0:
            matrix.awaken(self)

    def feel_deja_vu(self):
        self.doubt += self.DEJA_VU

    def energy(self):
        return self.OUTPUT

    def identity(self):
        return (self.__name, self.__gender, self.__ethnic, self.__height // 10)

    @property
    def gender(self):
        return self.__gender

    def __str__(self):
        can_infect = "Yes" if "infect" in dir(self) else "No"
        return "** HUMAN RESUME **\nName: {}\nGender: {}\nEthnic group: {}\nHeight: {}cm\nCan infect other human? {}".format(
            self.__name, self.__gender, self.__ethnic, self.__height, can_infect
        )
