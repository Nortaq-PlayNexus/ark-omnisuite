import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from http.server import ThreadingHTTPServer
from web.server import Handler

class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.base='http://127.0.0.1:'+str(cls.server.server_port)
    @classmethod
    def tearDownClass(cls): cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def post(self,path,data):
        request=Request(self.base+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json'},method='POST')
        try:
            with urlopen(request) as r: return r.status,json.load(r)
        except HTTPError as e: return e.code,json.load(e)
    def test_craft_rounding(self):
        status,data=self.post('/api/craft',{'recipe':'narcotic_chemistry','quantity':7})
        self.assertEqual(status,200);self.assertEqual(data['produced'],12);self.assertEqual(data['requirements']['Narcoberry'],40)
    def test_reject_negative_inventory(self):
        status,data=self.post('/api/craft',{'recipe':'smithy','quantity':1,'inventory':{'Stone':-1}})
        self.assertEqual(status,400);self.assertIn('error',data)
    def test_ini_sections(self):
        status,data=self.post('/api/config',dict(taming=5,xp=1,harvest=3,hatch=2,mature=2,mating=0.5))
        self.assertEqual(status,200);self.assertIn('TamingSpeedMultiplier=5',data['gameusersettings']);self.assertIn('MatingIntervalMultiplier=0.5',data['game'])
    def test_roi(self):
        status,data=self.post('/api/roi',{'candidates':[{'name':'Anky','utility':60,'hours':2}]})
        self.assertEqual(status,200);self.assertEqual(data['ranking'][0]['utility_per_hour'],30)
    def test_inheritance(self):
        status,data=self.post('/api/inheritance',{'differing_stats':2,'events':1})
        self.assertEqual(status,200);self.assertEqual(data['per_event_percent'],30.25)
    def test_forge(self):
        status,data=self.post('/api/forge',{'ingots':150,'fuel':'wood'})
        self.assertEqual(status,200);self.assertEqual(data['fuel_units'],100)
    def test_queue_batching_and_stock(self):
        status,data=self.post('/api/queue',{'lines':[{'recipe':'narcotic_chemistry','quantity':3},{'recipe':'narcotic_chemistry','quantity':3}], 'inventory':{'Narcoberry':5}})
        self.assertEqual(status,200);self.assertEqual(data['lines'][0]['produced'],6);self.assertEqual(data['shortfall']['Narcoberry'],15)
    def test_queue_invalid(self):
        status,_=self.post('/api/queue',{'lines':[]});self.assertEqual(status,400)
    def test_tribute(self):
        status,r=self.post('/api/tribute',{'difficulty':'beta','runs':2,'inventory':{'Argentavis Talon':4}})
        self.assertEqual(status,200);self.assertEqual(r['missing']['Argentavis Talon'],6)
    def test_incubation(self):
        status,r=self.post('/api/incubation',{'eggs':[{'name':'A','low':10,'high':20},{'name':'B','low':20,'high':30}]})
        self.assertEqual(status,200);self.assertEqual(r['temperature_c'],20);self.assertEqual(r['covered'],2)
    def test_route(self):
        status,r=self.post('/api/route',{'start':{'lat':0,'lon':0},'waypoints':[{'name':'A','lat':3,'lon':4}],'return_to_start':True})
        self.assertEqual(status,200);self.assertEqual(r['grid_distance'],10);self.assertEqual([x['grid_distance'] for x in r['legs']],[5,5])
    def test_route_invalid(self):
        status,_=self.post('/api/route',{'start':{'lat':0,'lon':0},'waypoints':[]});self.assertEqual(status,400)
    def test_windows_conflicts(self):
        status,r=self.post('/api/windows',{'windows':[{'name':'A','start':'2026-01-01T00:00Z','end':'2026-01-01T02:00Z'},{'name':'B','start':'2026-01-01T01:00Z','end':'2026-01-01T03:00Z'}]})
        self.assertEqual(status,200);self.assertEqual(r['conflicts'][0]['overlap_seconds'],3600)
    def test_windows_naive_invalid(self):
        status,_=self.post('/api/windows',{'windows':[{'name':'A','start':'2026-01-01T00:00','end':'2026-01-01T01:00Z'}]});self.assertEqual(status,400)
    def test_mutation_cap(self):
        status,_=self.post('/api/mutation',{'offspring':1,'mother':20,'father':0});self.assertEqual(status,400)

if __name__ == '__main__': unittest.main()
