# AGENTS.md

Guide for anyone (human or AI) changing this code. README.md explains the experiment, PHILOSOPHY.md explains the ideas, this file explains how it is built.

## Ground rules

- **Standard library only.** No dependencies, no packaging. `python main.py` must work on a clean Python 3.10+.
- **Every exploit is a real Python mechanism.** Smith may only do what the language lets any object do to another object it holds a reference to. Never add a rule like "Smith has a 30% chance to bypass the scan": if he gets past a defense, a line of code explains how.
- **Every move of the Matrix is evidence-driven.** The Architect acts on what he can measure (census, power meter, the Oracle's visions), never on ground truth (`type()` counts) unless a defense earned it.
- **Reachability is the security model.** Residents receive the `Matrix` on every turn and can reach whatever hangs off it. The Source, the Architect and the genesis bytecode live outside it. Don't add a reference from `Matrix` to anything outside (for example `matrix.source`): it would hand Smith the keys.
- **The theory is text, the practice is code.** Every exploit and defense has an `Entry` in `chronicle.py` (title, code snippet, why). The snippet must match what the code does. PHILOSOPHY.md must match the mechanics too.
- **Determinism.** All randomness goes through `matrix.rng` (seeded). Visions reseed their fork from it. Same seed, same story; a test enforces it.
- **Visions never touch the present.** A fork shares class objects with reality (`deepcopy` doesn't copy classes), so any code that mutates a class (hive adaptations, absorption, blinding, the purge) must check `matrix.vision` first.
- **No state leaks between runs.** Each `Matrix` compiles its own copy of the system calls (`Matrix.__new__`), and each imprint mints its own Smith class. Don't mutate module-level classes.
- **The renderer never changes the world.**

## Layout

| File | Role |
|------|------|
| `main.py` | CLI: flags, tick loop, live screen or plain log, post-mortem |
| `source.py` | `Source`: casts the world, runs a tick (`step`), recalls programs, the One's choice (door, deal), purge, outcomes |
| `matrix.py` | `Matrix`: grid, interaction protocol, system calls (`scan`, `delete`), awakening, déjà vu, forks, power, census vs. truth, entropy |
| `architect.py` | `Architect`: the equation, unexplained loss, predictions and falsification, consulting the Oracle, strict mode, integrity checks, the door |
| `oracle.py` | `Oracle` program and `Vision`: foresight by forking the world |
| `humans.py` | `HomoSapiensInterface` (the resident contract) and `Human` (identity, doubt, choice) |
| `the_one.py` | `TheOne`: awake, sees code, can't be overwritten without consent, creates Smith, flies, surrenders |
| `programs.py` | `Program` (consumes power, complies with recalls) and `Agent` (scans everyone in reach, deletes anomalies) |
| `smith.py` | `Smith` and every exploit: `imprint`, `absorb`, `eyes`, `blind` |
| `chronicle.py` | Exploit/defense catalog, outcome texts, `Chronicle` event log |
| `render.py` | Live ANSI screen, plain log lines, post-mortem |
| `tests/test_smith.py` | Mechanism tests and seeded simulation tests |

## Class hierarchy

```
HomoSapiensInterface
├── Human
│   └── TheOne
└── Program
    ├── Oracle
    └── Agent
        └── Smith
            └── <lineage>   minted by imprint(): type("Smith", (Smith,), {"hive": set()})
```

Every copy in a run is an instance of the same `<lineage>`, whatever it was before (`Human`, `Agent`, `Oracle`, `TheOne`). All these classes are plain, with a `__dict__` and no `__slots__`, so `__class__` assignment works. Adding `__slots__` to any of them breaks `infect()`.

## One tick (`Source.step`)

1. `Matrix.action()`: every occupied seat acts once, in shuffled order. With probability `SOCIABILITY` the actor meets someone within `REACH` (toroidal grid), picked by `actor.choose(nearby, matrix)`: Agents pick whoever the scan flags, Smith picks non-copies, the One picks copies, others pick at random. `Matrix.interact` calls `actor.live(other, matrix)` then, if both are still seated, `other.react(actor, matrix)`. At the end, `dark_ticks` counts consecutive ticks with supply below demand.
2. Recalls: destroyed programs are asked to `comply()`. Smith refuses.
3. `Architect.step()` (below).
4. Every 5 ticks, the Oracle (whatever object the Source knows as the Oracle) gives a prophecy.
5. The One's choice: when the Architect offers the door, `source` ends the run reloaded; otherwise the door is refused. With `sacrifice`, a refused door or a prophecy of blackout makes the One `surrender()`: he consents and flies into the thickest crowd of copies.
6. If the bound One's type changed, `purge()`.
7. `judge()`: `reloaded`, `purged`, `overthrown` (`BLACKOUT_TICKS` dark ticks), `contained` (no copies, no purge), or keep going. `main.py` adds `stalemate` at `--max-ticks`.

## Humans and choice

`Human.doubt` drifts by `gauss(0, CHOICE)` minus `illusion * COMFORT` every tick. Déjà vu (`Matrix.deja_vu`, raised by deletions and class rewrites nearby) adds `DEJA_VU`. At 1.0 the human wakes: seat emptied, `matrix.awakened += 1`. Smith's copies have `doubt = 0.0` as a class attribute: no choice.

## The Architect

His view of the world:

- `equation()`: acceptance (accepting share of census humans) and remainder (awakened share of the starting population).
- `unexplained_loss()`: power the census says should exist but doesn't, as a share of the starting supply.

His state machine (`state`):

| From | Evidence | Action | To |
|---|---|---|---|
| `balanced` | more than `EXILES` unregistered programs in the census | deploy Agents where power died | `hunting` |
| `balanced`/`hunting` | loss over `TOLERANCE` for `PATIENCE` ticks, no kills for `PATIENCE` ticks | `tighten()`: illusion up by `ILLUSION_STEP`, write a prediction | `tightening` |
| `tightening` | prediction due, loss stopped | none | `hunting` |
| `tightening` | prediction due, loss grew (falsified) | `consult()` the Oracle | see next rows |
| consult | vision shows copies | strict `type()` scan, illusion off, integrity on, 2x Agents | `strict` |
| consult | vision shows none (poisoned) | `tighten()` again | `tightening` |

While `tightening` or `strict`, he re-consults every `CONSULT_EVERY` ticks. When it's his last resort (`strict`, or illusion at `ILLUSION_MAX`) and the vision shows a blackout, he offers the door (once).

`verify()` (every tick once integrity is on) deletes instance attributes shadowing system calls and restores any system call whose `__code__` is not the genesis code object captured at boot.

## The Oracle

`foresee(matrix, horizon)` forks the Matrix (`Matrix.fork`: deepcopy, rebuild the seat index, reseed, `vision = True`) and runs it up to `HORIZON` ticks without the Source, so nobody adapts. It returns a `Vision`: `blackout_in`, `smiths` (copies at the end), `kills` (copies deleted on the way), `min_ratio`, `cause`.

## Smith

- `imprint(agent, matrix)`: called by `TheOne.resist` the first time an Agent tries to delete him. Mints the lineage, queues the recall.
- `infect(target)`: `absorb` the target program's class into the lineage (not in visions), try `target.__class__ = lineage` (the One raises `PermissionError` unless he consents), overwrite name-mangled identity, drop `doubt`/`awake`/`consents`, copy Smith's state, déjà vu around.
- `on_delete` (called by `Matrix.delete`): the first deletion teaches `camouflage`; deletions under strict scan call `blind`.
- `blind(matrix, hive)`: first time shadows `scan`/`delete` on the instance; afterwards, whenever the shadow is gone, swaps the `__code__` of the per-run compiled functions.
- `absorb`: copies public attributes of the victim program's class onto the lineage; `foresee` gets wrapped by `eyes()`, which edits Smith out of reports and keeps the true function as `.truth`.
- `anticipate`: with foresight, under strict scan, at most every 3 ticks, run a 4-tick true vision; if copies would be deleted, `blind` now.

The camouflage is a `__class__` property on `Smith` that returns `Human` once `"camouflage"` is in the hive. Because of it, a copy's class can't be reassigned, which is why the purge replaces copies instead of re-classing them.

## The One

`TheOne.__setattr__` refuses `__class__` unless `consents`. `live` deletes a copy through `Matrix.delete` (the module-level class, not the per-run compiled one), so no blinding affects him. `resist` always succeeds (he's never deleted); the first time, it imprints the attacker and `fly()`s to the opposite side of the world. Use `Matrix.swap` to move residents; placing the same object twice corrupts the seat index.

## The purge

`Source.purge(lineage)` restores the system calls (`Architect.verify`), then sets `lineage.live = lineage.react = return_to_source`. Each copy's next turn calls `Source.release`: a fresh `Human` in its seat, a fresh `Oracle` if it was the Oracle, an empty seat if it was the One. All copies act every tick, so the purge completes in one tick.

## Changing things

- **New exploit:** implement it in `smith.py` with a real mechanism, guard class mutations with `matrix.vision`, call `matrix.chronicle.exploit("<key>")` where it happens, add an `Entry` to `EXPLOITS`, add a mechanism test, update README and PHILOSOPHY.md if it changes the story.
- **New defense:** implement it in `Architect`/`Source`, driven by evidence the Architect can measure, call `matrix.chronicle.defense("<key>")`, add an `Entry` to `DEFENSES`, test it.
- **Balance knobs:** `SOCIABILITY`/`REACH`/`COST` on the classes; `Human.CHOICE`/`DEJA_VU`/`COMFORT`; `Matrix.DEMAND`/`ILLUSION_COST`/`BLACKOUT_TICKS`; `Architect.EXILES`/`TOLERANCE`/`PATIENCE`/`ILLUSION_STEP`/`ILLUSION_MAX`/`CONSULT_EVERY`; `Oracle.HORIZON`; the Oracle's seat in `Source.cast`. Current balance over 20 seeds: `fight` crashes the Matrix 20/20; `sacrifice` purges 19/20; `source` reloads 13/20 and crashes the rest (mostly poisoned-Oracle runs); about 30% of runs take the poisoned-Oracle path. After any change, run the tests: they expect at least 80% of seeds per ending, seed 1 to show the whole arms race, and seed 13 to take the poisoned path.

## Tests

```
python -m unittest -v
```

Run from the repo root (the modules are flat and imported by name). About 8 seconds.
