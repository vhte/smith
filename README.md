# Smith

An experiment that shows, at code level, how Agent Smith could overthrow the Matrix in theory, and why the Matrix's own intelligence can't stop him.

The Matrix here is a Python program with a mind of its own: an Architect who models the world as an equation and revises the model when its predictions fail, an Oracle who foresees by forking the whole world and running it ahead, Agents who hunt anomalies, and a Source that recalls programs and holds the reset. Smith beats them with real Python mechanisms, never a game rule. The ideas behind each mechanism are in [PHILOSOPHY.md](PHILOSOPHY.md).

## Run it

Python 3.10+ and the standard library only. Nothing to install.

```
python main.py                       # the One fights Smith: watch the Matrix fall
python main.py --choice sacrifice    # Revolutions: the One makes a deal with the machines
python main.py --choice source       # the five Ones before him: take the door, reload the Matrix
python main.py --seed 13             # replay a world (each run prints its seed); 13 is the poisoned Oracle
python main.py --plain               # log lines instead of the live screen (automatic when piped)
python main.py --help                # tick speed, grid size, Agents, max ticks, colors
```

## What you see

| Glyph | Who |
|-------|-----|
| `o` | Human (bluepill): produces power. Brighter means more doubt |
| `A` | Agent |
| `O` | The Oracle |
| `N` | The One |
| `S` | Smith, or a copy of him |
| `.` | Empty pod: someone was deleted or woke up |

Below the grid:

- **power**: supply vs. the machines' demand, and the current illusion level (it costs power). Three ticks below demand and the Matrix crashes.
- **truth** counts with `type()`, **census** counts with `isinstance()`. Once Smith learns camouflage, the census counts his copies as humans.
- **equation**: acceptance and remainder, what the Architect optimizes. It improves as Smith spreads.
- **choice**: identity entropy in bits. Smith drives it toward zero.
- **Architect**: what he believes, predicts and decides, in his words.
- **Oracle**: her latest prophecy.

Each new exploit or defense shows a card with the line of code behind it. The run ends with a post-mortem and the full timeline.

## The story the code tells

1. **The imprint.** Agent Smith tries to delete the One; the One destroys him from the inside, and something is copied over: the power to rewrite another program. Recalled by the Source, Smith refuses (he overrides `comply()`). He is the equation balancing itself.
2. **Replication.** `target.__class__ = type(self)`, name-mangled "private" identity overwritten, and touching a copy is enough to become one.
3. **Exiles, then a hunt.** The Matrix tolerates a few unregistered programs. When there are too many, the Architect sends Agents. A deleted copy teaches the hive (a set on the shared class) to lie to `isinstance()`; every copy is camouflaged at once.
4. **The error term.** Power goes missing while the census looks clean. Copies never doubt, so the Architect's acceptance has never been better. His model blames the remainder, he tightens the illusion, and the illusion burns power.
5. **Falsification.** His prediction fails, so he consults the Oracle. If she can still see, he learns the truth: strict `type()` scans, integrity checks, more Agents. If Smith has already taken her eyes, she tells him it's the remainder and he tightens again.
6. **The guard's code.** Smith shadows the system calls, then rewrites their bytecode. The Architect restores them every tick from a genesis copy outside Smith's reach. Smith can't win that, but every restore costs the Agents a tick of blindness, and he copies faster than they delete.
7. **The One's choice.** The Architect offers the door. What happens next is `--choice`.

| `--choice` | What the One does | Typical outcome |
|---|---|---|
| `fight` (default) | Refuses the door, deletes copies one by one | **The Matrix crashes** |
| `sacrifice` | Refuses the door, makes the deal, lets Smith take him | **The Source purges every copy through him** |
| `source` | Takes the door, like the five before him | **Reloaded: cycle seven**, unless a poisoned Oracle kept the Architect blind until too late |

## Tests

```
python -m unittest -v
```

Unit tests prove each mechanism (imprint, class rewrite, camouflage, absorption and censored sight, shadow then bytecode, integrity restore, the One's guard, visions not touching the present, the purge). Simulation tests check each ending over several seeds and that the same seed tells the same story. About 8 seconds.

## Architecture

See [AGENTS.md](AGENTS.md).

## License

GPL-3.0. See [LICENSE](LICENSE).
