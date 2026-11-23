"""Small bounded Discord slash-command parsers; core validates mechanics."""

def rows(value, width, limit, label):
    if not isinstance(value,str) or not value.strip() or len(value)>1000: raise ValueError(f'{label}: enter 1–1000 characters')
    parts=value.split(';')
    if len(parts)>limit: raise ValueError(f'{label}: at most {limit} entries')
    out=[]
    for entry in parts:
        fields=[x.strip() for x in entry.split('|')]
        if len(fields)!=width or any(not x for x in fields): raise ValueError(f'{label}: check field count and remove empty entries')
        out.append(fields)
    return out

def queue(value): return [{'recipe':a,'quantity':b} for a,b in rows(value,2,5,'Queue')]
def eggs(value): return [{'name':a,'low':b,'high':c} for a,b,c in rows(value,3,10,'Eggs')]
def pins(value): return [{'name':a,'lat':b,'lon':c} for a,b,c in rows(value,3,8,'Pins')]
def windows(value): return [{'name':a,'start':b,'end':c} for a,b,c in rows(value,3,4,'Windows')]
def tames(value): return [{'name':a,'utility':b,'hours':c} for a,b,c in rows(value,3,10,'Candidates')]
def inventory(value):
    if value is None or not value.strip(): return {}
    entries=rows(value,2,20,'Inventory');out={}
    for name,count in entries:
        if name in out: raise ValueError('Inventory item names must be unique')
        out[name]=count
    return out
