import unittest
from core.schedule import compare_windows
class ScheduleTests(unittest.TestCase):
 def test_offsets_and_overlap(self):
  r=compare_windows([{'name':'A','start':'2026-11-24T10:00:00Z','end':'2026-11-24T12:00:00Z'}, {'name':'B','start':'2026-11-24T22:00:00+11:00','end':'2026-11-25T00:00:00+11:00'}])
  self.assertEqual(r['conflicts'][0]['overlap_seconds'],3600)
  self.assertEqual(r['conflicts'][0]['start'],'2026-11-24T11:00:00Z')
  self.assertEqual(r['windows'][0]['discord_start'],'<t:1795514400:F>')
 def test_adjacent_and_duplicate_names(self):
  r=compare_windows([{'name':'A','start':'2026-01-01T00:00Z','end':'2026-01-01T01:00Z'},{'name':'A','start':'2026-01-01T01:00Z','end':'2026-01-01T02:00Z'}]);self.assertEqual(r['conflicts'],[]);self.assertEqual([x['index'] for x in r['windows']],[0,1])
 def test_multiple_overlaps(self):
  r=compare_windows([{'name':str(i),'start':'2026-01-01T00:00Z','end':'2026-01-01T01:00Z'} for i in range(3)]);self.assertEqual(len(r['conflicts']),3)
 def test_invalid(self):
  for windows in [[],[{'name':'A','start':'2026-01-01T00:00','end':'2026-01-01T01:00Z'}],[{'name':'A','start':'2026-01-01T00:00Z','end':'2026-01-01T00:00Z'}],[{}]*21]:
   with self.assertRaises(ValueError):compare_windows(windows)
