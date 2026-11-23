import unittest
from core.breeding import inheritance_odds
from core.forge import refining_forge
from core.crafting import craft_queue

class InheritanceTests(unittest.TestCase):
    def test_wiki_six_high_stats(self):
        # https://ark.fandom.com/wiki/Breeding table: six higher stats ~= 2.77%
        self.assertAlmostEqual(inheritance_odds(6,1)['per_event_percent'], 2.7681, places=4)
    def test_independent_events(self):
        r=inheritance_odds(2,2);self.assertAlmostEqual(r['per_event_percent'],30.25);self.assertAlmostEqual(r['at_least_one_percent'],51.3494,places=4)
    def test_all_stats_match(self): self.assertEqual(inheritance_odds(0,20)['at_least_one_percent'],100)
    def test_invalid(self):
        for n,events in [(-1,1),(8,1),(1,0),(True,1)]:
            with self.assertRaises(ValueError): inheritance_odds(n,events)

class ForgeTests(unittest.TestCase):
    def test_wiki_300_metal_example(self):
        # https://ark.fandom.com/wiki/Refining_Forge 300 metal / 150 ingots
        for fuel,needed in [('thatch',400),('wood',100),('sparkpowder',50),('anglergel',13)]:
            r=refining_forge(150,fuel);self.assertEqual((r['metal'],r['time_seconds'],r['fuel_units']),(300,3000,needed))
    def test_round_up(self): self.assertEqual(refining_forge(1,'wood')['fuel_units'],1)
    def test_bad(self):
        with self.assertRaises(ValueError):refining_forge(0,'wood')
        with self.assertRaises(ValueError):refining_forge(1,'unknown')

class QueueTests(unittest.TestCase):
    def test_shared_stock_is_subtracted_once(self):
        r=craft_queue([{'recipe':'smithy','quantity':1},{'recipe':'spyglass','quantity':1}],{'Wood':20,'Hide':5})
        self.assertEqual(r['requirements']['Wood'],35);self.assertEqual(r['shortfall']['Wood'],15)
        self.assertEqual(r['requirements']['Hide'],30);self.assertEqual(r['shortfall']['Hide'],25)
    def test_chemistry_split_lines_batch_together(self):
        r=craft_queue([{'recipe':'narcotic_chemistry','quantity':3},{'recipe':'narcotic_chemistry','quantity':3}])
        self.assertEqual(len(r['lines']),1);self.assertEqual(r['lines'][0]['batches'],1);self.assertEqual(r['requirements']['Narcoberry'],20)
    def test_ingot_stock_then_expand(self):
        r=craft_queue([{'recipe':'smithy','quantity':2}],{'Metal Ingot':3,'Metal':4},True)
        self.assertEqual(r['owned_ingots_used'],3);self.assertEqual(r['requirements']['Metal'],14);self.assertEqual(r['shortfall']['Metal'],10)
    def test_reject_bad(self):
        for q in [[],[{'recipe':'fake','quantity':1}],[{'recipe':'smithy','quantity':-1}]]:
            with self.assertRaises(ValueError): craft_queue(q)
        with self.assertRaises(ValueError): craft_queue([{'recipe':'smithy','quantity':1}],{'Stone':-1})
