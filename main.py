import argparse
import sys
from time import sleep

from render import Renderer
from source import CHOICES, Source

# This is the World running
# It demonstrates how Smith, unplugged, could overthrow the Matrix, and what the One's choice changes


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Watch Smith overthrow the Matrix, in theory.")
    parser.add_argument(
        "--choice", choices=CHOICES, default="fight",
        help="the One's choice: fight Smith (default), sacrifice himself in a deal with the machines, "
             "or take the Architect's door to the Source",
    )
    parser.add_argument("--seed", type=int, help="replay a specific world (printed on every run)")
    parser.add_argument("--width", type=int, default=40)
    parser.add_argument("--height", type=int, default=16)
    parser.add_argument("--agents", type=int, default=6, help="Agents on duty at boot")
    parser.add_argument("--tick", type=float, default=0.4, help="seconds per tick, for visual purposes")
    parser.add_argument("--max-ticks", type=int, default=400)
    parser.add_argument("--plain", action="store_true", help="log lines instead of a live screen")
    parser.add_argument("--no-color", action="store_true")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    live = not args.plain and sys.stdout.isatty()
    renderer = Renderer(color=live and not args.no_color)
    source = Source(args.width, args.height, args.agents, seed=args.seed, choice=args.choice)
    print("** MATRIX INITIATED ** seed {}".format(source.matrix.seed))

    printed = 0
    outcome = None
    while outcome is None:
        # The wheel of time keeps turning...
        outcome = source.step()
        if outcome is None and source.matrix.tick >= args.max_ticks:
            outcome = "stalemate"
        if live:
            print("\x1b[H\x1b[2J" + renderer.frame(source), flush=True)
            sleep(args.tick)
        else:
            for tick, text in source.chronicle.events[printed:]:
                print(renderer.event(tick, text))
            printed = len(source.chronicle.events)

    print(renderer.post_mortem(source, outcome))
    return outcome


if __name__ == "__main__":
    main()
