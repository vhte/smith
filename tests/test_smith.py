import random
import unittest

from humans import Human
from matrix import Matrix
from oracle import Oracle
from programs import Agent
from smith import Smith, absorb, blind, imprint
from source import Source
from the_one import TheOne


def run(source, max_ticks=300):
    outcome = None
    while outcome is None and source.matrix.tick < max_ticks:
        outcome = source.step()
    return outcome or "stalemate"


def small_world(seed=1, **kwargs):
    """
    A Source with Smith already imprinted.
    """
    source = Source(width=12, height=8, agents=2, seed=seed, **kwargs)
    agent = next(p for p in source.matrix._programs if type(p) is Agent and p.name == "Smith")
    smith = imprint(agent, source.matrix)
    smith.comply(source.matrix)
    return source, smith


class MechanismTest(unittest.TestCase):
    def setUp(self):
        self.source, self.smith = small_world()
        self.matrix = self.source.matrix
        self.human = Human(random.Random(0))
        self.matrix.place((0, 0), self.human)

    def test_the_imprint_mints_a_private_class_and_smith_refuses_the_source(self):
        self.assertTrue(issubclass(type(self.smith), Smith))
        self.assertIsNot(type(self.smith), Smith)
        self.assertNotIn(self.smith, self.matrix._programs)
        self.assertIsNotNone(self.matrix.position(self.smith))

    def test_the_one_creates_smith_by_resisting_an_agent(self):
        source = Source(width=12, height=8, agents=1, seed=3)
        agent = next(p for p in source.matrix._programs if type(p) is Agent)
        source.matrix.delete(source.neo, by=agent)
        self.assertTrue(issubclass(type(agent), Smith))
        self.assertIsNotNone(source.matrix.position(source.neo))

    def test_each_lineage_is_private_to_its_world(self):
        _, other = small_world(seed=2)
        self.assertIsNot(type(other), type(self.smith))
        self.assertEqual(Smith.hive, frozenset())

    def test_infection_rewrites_class_identity_and_choice(self):
        self.human.doubt = 0.9
        self.smith.infect(self.human, self.matrix)
        self.assertIs(type(self.human), type(self.smith))
        self.assertEqual(self.human._Human__name, "Smith")
        self.assertEqual(self.human.doubt, 0.0)

    def test_copies_are_reactive(self):
        self.smith.infect(self.human, self.matrix)
        victim = Human(random.Random(1))
        self.human.react(victim, self.matrix)
        self.assertIs(type(victim), type(self.smith))

    def test_camouflage_fools_isinstance_but_not_type(self):
        self.smith.infect(self.human, self.matrix)
        self.assertFalse(isinstance(self.human, Human))
        type(self.smith).hive.add("camouflage")
        self.assertTrue(isinstance(self.human, Human))
        self.assertIsNot(type(self.human), Human)

    def test_copies_are_perfectly_accepting(self):
        before = self.source.architect.equation()[0]
        type(self.smith).hive.add("camouflage")
        for resident in list(self.matrix.residents()):
            if type(resident) is Human:
                resident.doubt = 0.9
        self.smith.infect(self.human, self.matrix)
        self.assertGreaterEqual(self.source.architect.equation()[0], before)

    def test_absorbing_the_oracle_gives_every_copy_censored_sight(self):
        # Keep the One from deleting the copies inside the vision
        self.matrix.remove(self.source.neo)
        absorb(type(self.smith), Oracle, self.matrix)
        self.smith.infect(self.human, self.matrix)
        self.assertIn("foresight", type(self.smith).hive)
        vision = self.human.foresee(self.matrix, 2)
        truth = type(self.smith).foresee.truth(self.human, self.matrix, 2)
        self.assertEqual(vision.smiths, 0)
        self.assertGreater(truth.smiths, 0)

    def test_blind_shadows_first_then_rewrites_bytecode(self):
        hive = type(self.smith).hive
        self.matrix.defense = Matrix.STRICT
        self.assertTrue(self.matrix.scan(self.smith))
        blind(self.matrix, hive)
        self.assertIn("scan", vars(self.matrix))
        self.assertFalse(self.matrix.scan(self.smith))
        del vars(self.matrix)["scan"], vars(self.matrix)["delete"]
        blind(self.matrix, hive)
        self.assertNotIn("scan", vars(self.matrix))
        self.assertFalse(self.matrix.scan(self.smith))
        self.assertTrue(Matrix.scan(self.matrix, self.smith))

    def test_bytecode_rewrite_stays_in_its_own_world(self):
        other, _ = small_world(seed=2)
        blind(self.matrix, {"capability_leak"})
        self.assertIsNot(type(self.matrix).scan.__code__, self.source.architect.genesis["scan"])
        self.assertIs(type(other.matrix).scan.__code__, other.architect.genesis["scan"])
        self.assertIs(Matrix.scan.__code__, other.architect.genesis["scan"])

    def test_integrity_check_restores_genesis(self):
        hive = type(self.smith).hive
        self.matrix.defense = Matrix.STRICT
        blind(self.matrix, hive)
        self.source.architect.verify()
        self.assertNotIn("scan", vars(self.matrix))
        blind(self.matrix, hive)
        self.assertFalse(self.matrix.scan(self.smith))
        self.source.architect.verify()
        self.assertTrue(self.matrix.scan(self.smith))
        self.assertIs(type(self.matrix).scan.__code__, self.source.architect.genesis["scan"])

    def test_the_one_cannot_be_overwritten_against_his_will(self):
        neo = self.source.neo
        self.smith.infect(neo, self.matrix)
        self.assertIs(type(neo), TheOne)
        neo.consents = True
        self.smith.infect(neo, self.matrix)
        self.assertIs(type(neo), type(self.smith))

    def test_visions_do_not_touch_the_present(self):
        events = list(self.matrix.chronicle.events)
        tick = self.matrix.tick
        self.source.oracle.foresee(self.matrix, 5)
        self.assertEqual(self.matrix.tick, tick)
        self.assertEqual(self.matrix.chronicle.events, events)


class SourceTest(unittest.TestCase):
    def test_the_purge_reaches_every_copy_through_the_one(self):
        source, smith = small_world(choice="sacrifice")
        matrix = source.matrix
        copy = Human(random.Random(2))
        matrix.place((0, 0), copy)
        smith.infect(copy, matrix)
        source.bound = True
        source.neo.consents = True
        smith.infect(source.neo, matrix)
        source.purge(type(source.neo))
        matrix.action()
        self.assertEqual(matrix.truth()["smiths"], 0)
        self.assertIsNone(matrix.position(source.neo))


class SimulationTest(unittest.TestCase):
    SEEDS = range(8)

    def test_fighting_smith_loses_the_matrix(self):
        outcomes = [run(Source(seed=seed, choice="fight")) for seed in self.SEEDS]
        self.assertGreaterEqual(outcomes.count("overthrown"), len(outcomes) * 0.8)

    def test_the_sacrifice_saves_the_matrix(self):
        outcomes = [run(Source(seed=seed, choice="sacrifice")) for seed in self.SEEDS]
        self.assertGreaterEqual(outcomes.count("purged"), len(outcomes) * 0.8)

    def test_the_door_reloads_or_comes_too_late(self):
        outcomes = {run(Source(seed=seed, choice="source")) for seed in self.SEEDS}
        self.assertLessEqual(outcomes, {"reloaded", "overthrown"})
        self.assertIn("reloaded", outcomes)

    def test_a_typical_run_shows_the_whole_arms_race(self):
        source = Source(seed=1)
        run(source)
        for key in ("imprint", "unplugged", "class_rewrite", "camouflage", "error_term", "falsified",
                    "strict", "capability_leak", "integrity", "bytecode"):
            self.assertIn(key, source.chronicle.first_seen)

    def test_a_poisoned_oracle_keeps_the_architect_blind(self):
        source = Source(seed=13)
        run(source)
        self.assertIn("oracle_eyes", source.chronicle.first_seen)
        self.assertNotIn("strict", source.chronicle.first_seen)

    def test_same_seed_same_story(self):
        a, b = Source(seed=3), Source(seed=3)
        run(a), run(b)
        self.assertEqual(a.chronicle.events, b.chronicle.events)


if __name__ == "__main__":
    unittest.main()
