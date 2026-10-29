"""
Terminal output. Reads the Source and the Matrix, never changes them.
"""

import textwrap

from chronicle import CATALOG, EXPLOITS, OUTCOMES
from humans import Human
from oracle import Oracle
from programs import Agent
from smith import Smith
from the_one import TheOne

RESET = "\x1b[0m"
COLORS = {
    Human: "\x1b[37m",
    "doubt": "\x1b[1;97m",
    "calm": "\x1b[2;37m",
    Agent: "\x1b[1;36m",
    Smith: "\x1b[1;32m",
    TheOne: "\x1b[1;33m",
    Oracle: "\x1b[1;35m",
    None: "\x1b[90m",
    "title": "\x1b[1;32m",
    "exploit": "\x1b[1;31m",
    "defense": "\x1b[1;36m",
    "dim": "\x1b[2m",
}


class Renderer:
    def __init__(self, color=True, width=78):
        self.color = color
        self.width = width

    def paint(self, text, key):
        return "{}{}{}".format(COLORS[key], text, RESET) if self.color else text

    def frame(self, source):
        """
        One full screen: grid, power, the Architect's equation vs. the truth, the Architect's
        thinking, the Oracle's prophecy, the latest move and recent events.
        """
        matrix = source.matrix
        lines = [
            self.paint(" THE MATRIX ", "title")
            + " tick {:03d}   seed {}   the One: {}   agents: {}".format(
                matrix.tick, matrix.seed, source.choice, matrix.defense
            ),
            "",
        ]
        for row in matrix.get_grid():
            lines.append(" " + "".join(self.cell(resident) for resident in row))
        lines.append("")
        lines.append(self.gauge(matrix))
        lines.extend(self.counts(source))
        lines.append("")
        lines.extend(self.wrap("Architect: " + source.architect.thought))
        lines.extend(self.wrap("Oracle:    " + self.prophecy(source.prophecy)))
        lines.append("")
        lines.extend(self.card(matrix.chronicle.latest))
        lines.append("")
        for tick, text in matrix.chronicle.events[-4:]:
            lines.append(self.event(tick, text))
        return "\n".join(lines)

    def cell(self, resident):
        if resident is None:
            return self.paint(".", None)
        kind = type(resident)
        if kind is Human:
            return self.paint(kind.GLYPH, "doubt" if resident.doubt > 0.6 else "calm")
        for family in (TheOne, Smith, Oracle, Agent, Human):
            if issubclass(kind, family):
                return self.paint(kind.GLYPH, family)
        return kind.GLYPH

    def gauge(self, matrix, size=30):
        supply, demand = matrix.supply(), matrix.demand()
        ratio = supply / demand if demand else 1.0
        filled = max(0, min(size, round(size * ratio / 2)))
        bar = "#" * filled + "-" * (size - filled)
        status = "BLACKOUT {}/{}".format(matrix.dark_ticks, matrix.BLACKOUT_TICKS) if matrix.dark_ticks else "ok"
        return " power     [{}] {:.0f} / {:.0f} ({:.0%}) illusion {:.1f}  {}".format(
            bar, supply, demand, ratio, matrix.illusion, status
        )

    def counts(self, source):
        matrix = source.matrix
        truth, census = matrix.truth(), matrix.census()
        acceptance, remainder = source.architect.equation()
        smiths = self.paint("smiths {}".format(truth["smiths"]), Smith)
        return [
            " truth     humans {}  agents {}  {}  awakened {}".format(
                truth["humans"], truth["agents"], smiths, matrix.awakened
            ) + self.paint("   <- type()", "dim"),
            " census    humans {}  programs {}".format(census["humans"], census["programs"])
            + self.paint("   <- isinstance(): what the Matrix sees", "dim"),
            " equation  acceptance {:.1%}  remainder {:.1%}".format(acceptance, remainder)
            + self.paint("   <- what the Architect optimizes", "dim"),
            " choice    {:.2f} bits of identity entropy   exploits {}/{}   infections {}".format(
                matrix.entropy(),
                sum(1 for e in EXPLOITS if e.key in matrix.chronicle.first_seen),
                len(EXPLOITS),
                matrix.chronicle.infections,
            ),
        ]

    def prophecy(self, vision):
        if vision is None:
            return "..."
        if vision.blackout_in:
            seen = "Everything that has a beginning has an end: blackout in {} ticks.".format(vision.blackout_in)
        else:
            seen = "The grid holds for the next {} ticks (lowest {:.0%}).".format(vision.horizon, vision.min_ratio)
        if vision.smiths:
            seen += " I see {} of him.".format(vision.smiths)
        return seen

    def wrap(self, text):
        return textwrap.wrap(text, self.width, initial_indent=" ", subsequent_indent="            ")

    def card(self, key):
        if key is None:
            return [self.paint(" Waiting for the first move...", "dim")]
        entry = CATALOG[key]
        kind = "exploit" if entry in EXPLOITS else "defense"
        lines = [" " + self.paint("{}: {}".format(kind.upper(), entry.title), kind)]
        lines.extend("   " + self.paint(code, "dim") for code in entry.code.splitlines())
        lines.extend(textwrap.wrap(entry.why, self.width, initial_indent=" ", subsequent_indent=" "))
        return lines

    def event(self, tick, text):
        if text.startswith("EXPLOIT"):
            text = self.paint(text, "exploit")
        elif text.startswith("DEFENSE"):
            text = self.paint(text, "defense")
        return " t{:03d} {}".format(tick, text)

    def post_mortem(self, source, outcome):
        matrix = source.matrix
        title, verdict = OUTCOMES[outcome]
        truth = matrix.truth()
        acceptance, remainder = source.architect.equation()
        lines = [
            "",
            self.paint("** {} **".format(title), "title"),
            "tick {}, seed {}, the One chose: {}".format(matrix.tick, matrix.seed, source.choice),
            "humans {}, smiths {}, awakened {}, infections {}, integrity restores {}".format(
                truth["humans"], truth["smiths"], matrix.awakened, matrix.chronicle.infections,
                matrix.chronicle.restorations,
            ),
            "the Architect's equation: acceptance {:.1%}, remainder {:.1%}; identity entropy {:.2f} bits".format(
                acceptance, remainder, matrix.entropy()
            ),
            "",
        ]
        lines.extend(textwrap.wrap(verdict, self.width))
        lines.extend(["", "How it happened:"])
        for tick, entry in matrix.chronicle.timeline():
            kind = "exploit" if entry in EXPLOITS else "defense"
            lines.append(
                "  t{:03d} {} {}".format(tick, self.paint("{:7}".format(kind.upper()), kind), entry.title)
            )
            lines.extend("         " + self.paint(code, "dim") for code in entry.code.splitlines())
        return "\n".join(lines)
