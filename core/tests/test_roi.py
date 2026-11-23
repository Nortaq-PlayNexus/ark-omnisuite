import unittest
from core.roi import rank_tames
class RoiTests(unittest.TestCase):
    def test_rank(self):
        r=rank_tames([{'name':'A','utility':40,'hours':2},{'name':'B','utility':60,'hours':1}])
        self.assertEqual([x['name'] for x in r['ranking']],['B','A']);self.assertEqual(r['ranking'][1]['utility_per_hour'],20)
    def test_invalid(self):
        for candidates in [[],[{'name':'A','utility':1,'hours':0}],[{'name':'A','utility':'NaN','hours':1}],[{'name':'A','utility':True,'hours':1}]]:
            with self.assertRaises(ValueError):rank_tames(candidates)
    def test_ties_are_stable(self):
        r=rank_tames([{'name':'A','utility':5,'hours':1},{'name':'B','utility':5,'hours':1}])
        self.assertEqual([x['name'] for x in r['ranking']],['A','B'])
    def test_rank_before_display_rounding(self):
        r=rank_tames([{'name':'lower','utility':1,'hours':1},{'name':'higher','utility':1.001,'hours':1}])
        self.assertEqual(r['ranking'][0]['name'],'higher')
