import math
import unittest
from core import ingots, mutation_odds, readiness, advisor

class CoreTests(unittest.TestCase):
    def test_ingots_wiki_reference(self):
        # https://ark.fandom.com/wiki/Metal_Ingot — 2 Metal per ingot.
        self.assertEqual(ingots(15)['metal'], 30)
    def test_ingots_reject_bad_input(self):
        for x in [0,-1,1.5,'a',True]:
            with self.assertRaises(ValueError): ingots(x)
    def test_mutation_one_baby(self):
        self.assertAlmostEqual(mutation_odds(1)['probability_percent'], 7.314, places=3)
    def test_mutation_many(self):
        self.assertAlmostEqual(mutation_odds(10)['probability_percent'], round(100*(1-0.975**30),3))
    def test_mutation_caps(self):
        for a,b in [(20,0),(0,20),(20,20)]:
            with self.assertRaises(ValueError): mutation_odds(1,a,b)
    def test_readiness(self): self.assertEqual(readiness([True,False,True,False,True])['score'],60)
    def test_readiness_rejects(self):
        with self.assertRaises(ValueError): readiness([1,0])
    def test_advisor(self):
        self.assertEqual(len(advisor(30,True,True)['tasks']),3)
    def test_advisor_bad(self):
        with self.assertRaises(ValueError): advisor(0, True, False)

if __name__ == '__main__': unittest.main()

class CraftingTests(unittest.TestCase):
    def test_smithy_dododex(self):
        from core.crafting import craft
        # https://www.dododex.com/item/1726/smithy
        self.assertEqual(craft('smithy',2)['requirements'], {'Metal Ingot':10,'Stone':100,'Wood':60,'Hide':40})
    def test_smithy_ingots_expansion_and_stock(self):
        from core.crafting import craft
        r=craft('smithy',2,{'Metal Ingot':3,'Metal':4,'Stone':100},True)
        self.assertEqual(r['requirements']['Metal'],14)
        self.assertEqual(r['shortfall']['Metal'],10)
        self.assertEqual(r['shortfall']['Stone'],0)
    def test_chemistry_batches(self):
        from core.crafting import craft
        # https://ark.wiki.gg/wiki/Chemistry_Bench 20 berries + 4 meat -> 6 narcotic
        r=craft('narcotic_chemistry',7)
        self.assertEqual((r['batches'],r['produced'],r['surplus']),(2,12,5))
        self.assertEqual(r['requirements'],{'Narcoberry':40,'Spoiled Meat':8})
    def test_invalid(self):
        from core.crafting import craft
        with self.assertRaises(ValueError): craft('nope',1)
        with self.assertRaises(ValueError): craft('smithy',0)
        with self.assertRaises(ValueError): craft('smithy',1,{'Stone':-1})
    def test_ini(self):
        from core.config import ini_snippets
        x=ini_snippets(dict(taming=5,xp=2,harvest=3,hatch=10,mature=10,mating=0.3))
        self.assertIn('TamingSpeedMultiplier=5\n',x['gameusersettings'])
        self.assertIn('MatingIntervalMultiplier=0.3\n',x['game'])
        with self.assertRaises(ValueError): ini_snippets(dict(taming='1\nInjected=yes',xp=1,harvest=1,hatch=1,mature=1,mating=1))
