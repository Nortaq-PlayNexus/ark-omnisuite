"""Offline tests: instantiate the real discord.py command tree and invoke callbacks with fake interactions."""
import os, tempfile, unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock
from bot.store import PlanStore, MAX_PLANS
from bot import parsing

try:
 import discord
 from bot.main import create_client
except ImportError:
 discord=None

class ParsingTests(unittest.TestCase):
 def test_valid(self):
  self.assertEqual(parsing.queue('smithy|2; spyglass|1')[1]['recipe'],'spyglass')
  self.assertEqual(parsing.inventory('Wood|3;Stone|5'),{'Wood':'3','Stone':'5'})
  self.assertEqual(parsing.pins('A|3|4')[0]['lat'],'3')
  self.assertEqual(parsing.windows('event|2027-01-01T00:00Z|2027-01-01T01:00Z')[0]['name'],'event')
 def test_bad(self):
  for fun, text in [(parsing.queue,''),(parsing.queue,'smithy|1;'),(parsing.eggs,'A|1'),(parsing.inventory,'Wood|1;Wood|2'),(parsing.pins,';'.join('a|1|2' for _ in range(9))),(parsing.windows,'a'*1001)]:
   with self.subTest(text=text):
    with self.assertRaises(ValueError): fun(text)

class StoreTests(unittest.TestCase):
 def setUp(self): self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'db'/'omni.sqlite3';self.s=PlanStore(self.path)
 def tearDown(self): self.tmp.cleanup()
 def test_isolation_edit_persistence_delete(self):
  n=self.s.add(100,1,'  metal\nrun  ');self.assertEqual(self.s.list(100,1)[0]['text'],'metal run')
  self.assertEqual(self.s.list(100,2),[]);self.assertEqual(self.s.list(101,1),[]);self.assertEqual(self.s.list(0,1),[])
  self.assertFalse(self.s.edit(100,2,n,'steal'));self.assertFalse(self.s.set_done(101,1,n,True));self.assertFalse(self.s.delete(0,1,n))
  self.assertTrue(self.s.edit(100,1,n,'new'));self.assertTrue(self.s.set_done(100,1,n,True))
  self.assertEqual(PlanStore(self.path).list(100,1),[{'id':n,'text':'new','done':True}])
  self.assertTrue(self.s.set_done(100,1,n,False));self.assertTrue(self.s.delete(100,1,n));self.assertFalse(self.s.delete(100,1,n))
 def test_validation(self):
  for v in ('','  ','x'*121):
   with self.assertRaises(ValueError):self.s.add(1,1,v)
  with self.assertRaises(ValueError):self.s.delete(1,1,2**80)
  with self.assertRaises(ValueError):self.s.list(1,0)
 def test_limit_and_concurrency(self):
  def add(i):
   try:self.s.add(1,1,'task '+str(i));return True
   except ValueError:return False
  with ThreadPoolExecutor(max_workers=8) as pool: successes=list(pool.map(add,range(MAX_PLANS+10)))
  self.assertEqual(sum(successes),MAX_PLANS);self.assertEqual(len(self.s.list(1,1)),MAX_PLANS)
  self.assertEqual(self.s.add(1,2,'another user')>0,True)
 def test_file_permissions(self):
  if os.name=='posix':self.assertEqual(self.path.stat().st_mode & 0o777,0o600)

def fake_interaction(user=1,guild=100):
 return SimpleNamespace(user=SimpleNamespace(id=user),guild_id=guild,response=SimpleNamespace(send_message=AsyncMock(),defer=AsyncMock()),followup=SimpleNamespace(send=AsyncMock()))

@unittest.skipIf(discord is None,'discord.py not installed')
class CommandTests(unittest.IsolatedAsyncioTestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.client=create_client(Path(self.tmp.name)/'bot.sqlite3');self.tree=self.client.omni_tree
 def tearDown(self):self.tmp.cleanup()
 def command(self,name):return self.tree.get_command(name)
 async def call(self,name,*args,**kwargs):
  i=fake_interaction();await self.command(name).callback(i,*args,**kwargs);return i
 def test_registration(self):
  self.assertEqual({c.name for c in self.tree.get_commands()},{'omni','ingots','mutation','inheritance','forge','craft','tribute','queue','incubate','route','windows','rates','readiness','advisor','tamecompare','plans'})
  self.assertEqual({x.name for x in self.command('plans').commands},{'add','list','edit','done','remove'})
  for c in self.tree.walk_commands(): self.assertLessEqual(len(c.description),100)
  for c in self.tree.get_commands(): self.assertEqual(c.to_dict(self.tree)['name'],c.name)
 async def test_queue_and_visibility(self):
  i=await self.call('queue','smithy|1;spyglass|1',stock='Wood|20',public=True)
  kw=i.response.send_message.await_args.kwargs;self.assertFalse(kw['ephemeral']);self.assertFalse(kw['allowed_mentions'].everyone);self.assertIn('Wood: 35 required → 15 missing',kw['embed'].description);self.assertIn('https://',kw['embed'].description)
  bad_stock=await self.call('queue','smithy|1',stock='wood|10');self.assertIn('case-sensitive',bad_stock.response.send_message.await_args.kwargs['embed'].description)
  i=await self.call('queue','bad|2',public=True);kw=i.response.send_message.await_args.kwargs;self.assertTrue(kw['ephemeral']);self.assertEqual(kw['embed'].title,'OMNI // INPUT ERROR')
 async def test_setup_hook_sync_modes(self):
  from unittest.mock import patch
  with patch.object(self.tree,'sync',new_callable=AsyncMock) as sync:
   await self.client.setup_hook();sync.assert_awaited_once_with()
  guild_client=create_client(Path(self.tmp.name)/'guild.sqlite3',123)
  with patch.object(guild_client.omni_tree,'sync',new_callable=AsyncMock) as sync,patch.object(guild_client.omni_tree,'copy_global_to') as copy:
   await guild_client.setup_hook();self.assertEqual(sync.await_args.kwargs['guild'].id,123);self.assertEqual(copy.call_args.kwargs['guild'].id,123)
 async def test_each_new_calculation(self):
  cases=[('incubate',('A|10|20;B|20|30',),'20.0 °C'),('route',(0.0,0.0,'A|3|4'),'5.0 grid units'),('windows',('A|2027-01-01T00:00Z|2027-01-01T01:00Z;B|2027-01-01T00:30Z|2027-01-01T02:00Z',),'1800.0 sec'),('rates',(),'TamingSpeedMultiplier=1'),('readiness',(True,False,True,False,True),'60/100'),('advisor',(30,),'short objective'),('tamecompare',('A|20|1;B|80|2',),'B: 40.0')]
  for name,args,expected in cases:
   with self.subTest(command=name):
    i=await self.call(name,*args);kw=i.response.send_message.await_args.kwargs;self.assertTrue(kw['ephemeral']);self.assertIn(expected,kw['embed'].description)
 async def test_original_commands(self):
  cases=[('ingots',(15,),'30 Metal'),('mutation',(1,),'7.314%'),('inheritance',(2,1),'30.25%'),('forge',(150,'wood'),'100 wood'),('craft',('smithy',1),'Stone'),('tribute',('beta',2),'10 required')]
  for name,args,expected in cases:
   with self.subTest(command=name):
    i=await self.call(name,*args);self.assertIn(expected,i.response.send_message.await_args.kwargs['embed'].description)
 async def test_storage_error_does_not_leak_details(self):
  from unittest.mock import patch
  with patch('bot.main.PlanStore') as mock:
   mock.return_value.add.side_effect=RuntimeError('sensitive internal error')
   client=create_client(Path(self.tmp.name)/'unused.sqlite3')
   interaction=fake_interaction();await client.omni_tree.get_command('plans').get_command('add').callback(interaction,'test')
   msg=interaction.followup.send.await_args.kwargs
   self.assertTrue(msg['ephemeral']);self.assertNotIn('sensitive',msg['embed'].description)
 async def test_plans_pagination(self):
  group=self.command('plans')
  for i in range(6): await group.get_command('add').callback(fake_interaction(),'entry '+str(i))
  first=fake_interaction();await group.get_command('list').callback(first)
  self.assertIn('Page 1/2',first.followup.send.await_args.kwargs['embed'].description)
  second=fake_interaction();await group.get_command('list').callback(second,2)
  self.assertIn('entry 5',second.followup.send.await_args.kwargs['embed'].description)
  invalid=fake_interaction();await group.get_command('list').callback(invalid,3)
  self.assertIn('Page must be',invalid.followup.send.await_args.kwargs['embed'].description)
 async def test_no_mentions_and_escaping(self):
  i=await self.call('incubate','@everyone **A**|0|1')
  kw=i.response.send_message.await_args.kwargs;self.assertFalse(kw['allowed_mentions'].everyone);self.assertIn('\\*\\*A\\*\\*',kw['embed'].description)
 async def test_plans_crud_and_scope(self):
  group=self.command('plans');a=fake_interaction()
  await group.get_command('add').callback(a,'secret @everyone **test**')
  a.response.defer.assert_awaited_once_with(ephemeral=True,thinking=True)
  message=a.followup.send.await_args.kwargs;self.assertTrue(message['ephemeral']);self.assertFalse(message['allowed_mentions'].everyone);self.assertIn('#1',message['embed'].description)
  b=fake_interaction(user=2);await group.get_command('list').callback(b);self.assertIn('No notes yet',b.followup.send.await_args.kwargs['embed'].description)
  a=fake_interaction();await group.get_command('list').callback(a);self.assertIn('\\*\\*test\\*\\*',a.followup.send.await_args.kwargs['embed'].description)
  b=fake_interaction(user=2);await group.get_command('remove').callback(b,1);self.assertIn('not found',b.followup.send.await_args.kwargs['embed'].description)
  a=fake_interaction();await group.get_command('edit').callback(a,1,'changed');self.assertIn('Updated',a.followup.send.await_args.kwargs['embed'].description)
  a=fake_interaction();await group.get_command('done').callback(a,1);self.assertIn('complete',a.followup.send.await_args.kwargs['embed'].description)
  a=fake_interaction();await group.get_command('remove').callback(a,1);self.assertIn('Removed',a.followup.send.await_args.kwargs['embed'].description)

if __name__=='__main__':unittest.main()
