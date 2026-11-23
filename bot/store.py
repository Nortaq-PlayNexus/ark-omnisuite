"""Private, owner-scoped personal notes stored in a local SQLite file."""
from contextlib import closing
from pathlib import Path
import os, sqlite3

MAX_PLANS = 15

class PlanStore:
    def __init__(self, path):
        self.path=Path(path).expanduser()
        self.path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        try:
            fd=os.open(str(self.path),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
            os.close(fd)
        except FileExistsError: pass
        with closing(self._connect()) as c, c:
            c.execute('CREATE TABLE IF NOT EXISTS plans (id INTEGER PRIMARY KEY AUTOINCREMENT, guild TEXT NOT NULL, owner TEXT NOT NULL, text TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0,1)))')
            c.execute('CREATE INDEX IF NOT EXISTS plans_owner ON plans(guild,owner,id)')
    def _connect(self): return sqlite3.connect(str(self.path), timeout=5)
    @staticmethod
    def _scope(guild,owner):
        if isinstance(guild,bool) or isinstance(owner,bool) or not isinstance(guild,int) or not isinstance(owner,int) or guild<0 or owner<=0: raise ValueError('Invalid identity')
        return str(guild),str(owner)
    @staticmethod
    def _text(text):
        if not isinstance(text,str): raise ValueError('Note text is required')
        text=' '.join(text.split())
        if not text or len(text)>120: raise ValueError('Note must be 1–120 characters')
        return text
    @staticmethod
    def _id(note_id):
        if isinstance(note_id,bool) or not isinstance(note_id,int) or not 1<=note_id<=9223372036854775807: raise ValueError('Note ID must be a positive 64-bit integer')
        return note_id
    def add(self,guild,owner,text):
        scope=self._scope(guild,owner);text=self._text(text)
        with closing(self._connect()) as c, c:
            c.execute('BEGIN IMMEDIATE')
            count=c.execute('SELECT COUNT(*) FROM plans WHERE guild=? AND owner=?',scope).fetchone()[0]
            if count>=MAX_PLANS: raise ValueError(f'Limit is {MAX_PLANS} notes in this context; remove one first')
            return c.execute('INSERT INTO plans(guild,owner,text) VALUES (?,?,?)',(*scope,text)).lastrowid
    def list(self,guild,owner):
        scope=self._scope(guild,owner)
        with closing(self._connect()) as c:
            return [{'id':i,'text':t,'done':bool(d)} for i,t,d in c.execute('SELECT id,text,done FROM plans WHERE guild=? AND owner=? ORDER BY id',scope)]
    def edit(self,guild,owner,note_id,text):
        scope=self._scope(guild,owner);note_id=self._id(note_id);text=self._text(text)
        with closing(self._connect()) as c, c:
            return bool(c.execute('UPDATE plans SET text=? WHERE guild=? AND owner=? AND id=?',(text,*scope,note_id)).rowcount)
    def set_done(self,guild,owner,note_id,done):
        scope=self._scope(guild,owner);note_id=self._id(note_id)
        if not isinstance(done,bool): raise ValueError('done must be true or false')
        with closing(self._connect()) as c, c:
            return bool(c.execute('UPDATE plans SET done=? WHERE guild=? AND owner=? AND id=?',(int(done),*scope,note_id)).rowcount)
    def delete(self,guild,owner,note_id):
        scope=self._scope(guild,owner);note_id=self._id(note_id)
        with closing(self._connect()) as c, c:
            return bool(c.execute('DELETE FROM plans WHERE guild=? AND owner=? AND id=?',(*scope,note_id)).rowcount)
