import itertools, math, unittest
from core.survivor_tools import broodmother_manifest, incubation_mixer, waypoint_route

class ManifestTests(unittest.TestCase):
 def test_gamma_no_apex(self):
  r=broodmother_manifest('gamma',2);self.assertEqual(len(r['required']),3);self.assertEqual(r['required']['Artifact of the Hunter'],2)
 def test_alpha_missing(self):
  r=broodmother_manifest('alpha',2,{'Argentavis Talon':15,'Artifact of the Hunter':4})
  self.assertEqual(r['required']['Argentavis Talon'],20);self.assertEqual(r['missing']['Argentavis Talon'],5);self.assertEqual(r['missing']['Artifact of the Hunter'],0)
 def test_beta_source(self):
  # https://ark.wiki.gg/wiki/Broodmother_Arena 1 each artifact + 5 each apex
  r=broodmother_manifest('beta');self.assertEqual(r['required']['Sauropod Vertebra'],5);self.assertEqual(r['required']['Artifact of the Massive'],1)
 def test_validation(self):
  for diff,runs,stock in [('invalid',1,{}),('alpha',0,{}),('beta',1,{'Argentavis Talon':-1})]:
   with self.assertRaises(ValueError):broodmother_manifest(diff,runs,stock)

class MixerTests(unittest.TestCase):
 def test_overlap_and_disjoint(self):
  r=incubation_mixer([{'name':'A','low':10,'high':20},{'name':'B','low':20,'high':25},{'name':'C','low':30,'high':40}])
  self.assertEqual((r['temperature_c'],r['covered'],r['included'],r['excluded']),(20,2,['A','B'],['C']))
 def test_tie_is_deterministic(self):
  r=incubation_mixer([{'name':'A','low':0,'high':1},{'name':'B','low':5,'high':6}]);self.assertEqual(r['temperature_c'],0)
 def test_invalid(self):
  for items in [[],[{'name':'X','low':5,'high':4}],[{'name':'X','low':'NaN','high':4}]]:
   with self.assertRaises(ValueError):incubation_mixer(items)

class RouteTests(unittest.TestCase):
 def test_best_route_vs_brute_force(self):
  pins=[{'name':str(i),'lat':lat,'lon':lon} for i,(lat,lon) in enumerate([(10,20),(70,30),(5,90),(12,14),(33,41)])]
  origin={'lat':50,'lon':50};r=waypoint_route(origin,pins,True)
  def cost(order):
   pts=[(50,50)]+[(p['lat'],p['lon']) for p in order]+[(50,50)]
   return sum(math.dist(a,b) for a,b in zip(pts,pts[1:]))
  self.assertAlmostEqual(r['grid_distance'],round(min(cost(x) for x in itertools.permutations(pins)),3))
 def test_one_pin_return(self):
  r=waypoint_route({'lat':0,'lon':0},[{'name':'A','lat':3,'lon':4}],True);self.assertEqual(r['grid_distance'],10)
 def test_legs_and_cumulative(self):
  r=waypoint_route({'lat':0,'lon':0},[{'name':'A','lat':3,'lon':4},{'name':'B','lat':6,'lon':8}],True)
  self.assertEqual([leg['grid_distance'] for leg in r['legs']],[5,5,10])
  self.assertEqual([leg['cumulative_grid_distance'] for leg in r['legs']],[5,10,20])
  self.assertEqual(r['legs'][-1]['to']['name'],'Start');self.assertEqual(r['grid_distance'],20)
 def test_no_return_and_same_location(self):
  r=waypoint_route({'lat':5,'lon':5},[{'name':'On start','lat':5,'lon':5}],False)
  self.assertEqual(len(r['legs']),1);self.assertEqual(r['legs'][0]['grid_distance'],0)
 def test_invalid(self):
  with self.assertRaises(ValueError):waypoint_route({'lat':0,'lon':0},[])
  with self.assertRaises(ValueError):waypoint_route({'lat':0,'lon':0},[{'name':'A','lat':101,'lon':0}])
  with self.assertRaises(ValueError):waypoint_route({'lat':0,'lon':0},[{'name':'A','lat':0,'lon':0}]*9)
