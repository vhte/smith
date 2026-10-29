from collections import namedtuple

from programs import Program

# What the Oracle saw: in how many ticks the grid fails (None: not within the horizon), how many
# copies of Smith exist at the end of the vision, how many were deleted on the way, the lowest
# supply/demand ratio, and the cause she names.
Vision = namedtuple("Vision", "horizon blackout_in smiths kills min_ratio cause")


class Oracle(Program):
    """
    The intuitive program. Where the Architect models the world, she watches it.

    Her foresight is not magic: she forks the whole Matrix and lets the copy run ahead. She sees
    the path the world is on, not the choices nobody has made yet: in a vision nobody adapts.
    """

    GLYPH = "O"
    COST = 0.2
    SOCIABILITY = 0.2
    HORIZON = 12

    def __init__(self):
        super().__init__("Oracle")

    def foresee(self, matrix, horizon=None):
        horizon = horizon or self.HORIZON
        fork = matrix.fork()
        kills = fork.smith_deletions
        blackout_in = None
        min_ratio = float("inf")
        for step in range(1, horizon + 1):
            fork.action()
            min_ratio = min(min_ratio, fork.supply() / fork.demand())
            if fork.dark_ticks >= fork.BLACKOUT_TICKS:
                blackout_in = step
                break
        smiths = fork.truth()["smiths"]
        if smiths:
            cause = "smith"
        elif fork.awakened > matrix.awakened:
            cause = "remainder"
        else:
            cause = "none"
        return Vision(horizon, blackout_in, smiths, fork.smith_deletions - kills, min_ratio, cause)
